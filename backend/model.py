"""
머신러닝 모델 모듈
- Prophet 시계열 예측 모델
- SHAP 기반 예측 근거 분석
"""
import pandas as pd
import numpy as np
from prophet import Prophet
from typing import Dict, Tuple, Optional
import pickle
import os
from datetime import datetime, timedelta


def prepare_prophet_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prophet 모델 입력 형식으로 데이터 변환
    
    Args:
        df: 월별 평균가격 DataFrame (year_month, avg_price 컬럼 포함)
    
    Returns:
        Prophet 형식 DataFrame (ds, y 컬럼)
    """
    df_prophet = df.copy()
    
    # year_month를 datetime으로 변환
    df_prophet['ds'] = pd.to_datetime(df_prophet['year_month'] + '-01')
    df_prophet['y'] = df_prophet['avg_price']
    
    # 필요한 컬럼만 선택
    df_prophet = df_prophet[['ds', 'y']].copy()
    
    return df_prophet


def train_prophet_model(df: pd.DataFrame, **prophet_params) -> Prophet:
    """
    Prophet 모델 학습
    
    Args:
        df: Prophet 형식 DataFrame (ds, y 컬럼)
        **prophet_params: Prophet 모델 파라미터
    
    Returns:
        학습된 Prophet 모델
    """
    # 기본 파라미터 설정
    default_params = {
        'yearly_seasonality': True,
        'weekly_seasonality': False,  # 월 단위 데이터이므로 주간 계절성 불필요
        'daily_seasonality': False,
        'seasonality_mode': 'multiplicative',  # 곱셈 계절성 (가격 변동에 적합)
        'changepoint_prior_scale': 0.05,  # 변화점 감지 민감도
    }
    
    # 사용자 파라미터로 덮어쓰기
    default_params.update(prophet_params)
    
    model = Prophet(**default_params)
    model.fit(df)
    
    return model


def predict_current_and_next_month(model: Prophet, last_date: datetime) -> Dict:
    """
    이번달과 다음달 가격 예측
    
    Args:
        model: 학습된 Prophet 모델
        last_date: 마지막 데이터 날짜
    
    Returns:
        예측 결과 딕셔너리
        {
            'current_month': {날짜, 예측값, 하한, 상한},
            'next_month': {날짜, 예측값, 하한, 상한}
        }
    """
    from datetime import datetime
    
    # 현재 날짜 기준으로 이번달과 다음달 계산
    now = datetime.now()
    current_month = datetime(now.year, now.month, 1)
    
    # 다음달 날짜 계산
    if now.month == 12:
        next_month = datetime(now.year + 1, 1, 1)
    else:
        next_month = datetime(now.year, now.month + 1, 1)
    
    # 예측 기간 생성 (이번달과 다음달)
    future = pd.DataFrame({'ds': [current_month, next_month]})
    
    # 예측 수행
    forecast = model.predict(future)
    
    result = {
        'current_month': {
            'date': current_month,
            'predicted_price': forecast['yhat'].iloc[0],
            'lower_bound': forecast['yhat_lower'].iloc[0],
            'upper_bound': forecast['yhat_upper'].iloc[0],
        },
        'next_month': {
            'date': next_month,
            'predicted_price': forecast['yhat'].iloc[1],
            'lower_bound': forecast['yhat_lower'].iloc[1],
            'upper_bound': forecast['yhat_upper'].iloc[1],
        }
    }
    
    return result


def predict_next_month(model: Prophet, last_date: datetime) -> Dict:
    """
    다음달 가격 예측 (기존 호환성 유지)
    
    Args:
        model: 학습된 Prophet 모델
        last_date: 마지막 데이터 날짜
    
    Returns:
        예측 결과 딕셔너리 (날짜, 예측값, 하한, 상한)
    """
    predictions = predict_current_and_next_month(model, last_date)
    return predictions['next_month']


def generate_forecast_dataframe(model: Prophet, periods: int = 12, start_date: Optional[datetime] = None) -> pd.DataFrame:
    """
    향후 여러 기간 예측 데이터 생성
    
    Args:
        model: 학습된 Prophet 모델
        periods: 예측할 기간 수 (개월)
        start_date: 시작 날짜 (None이면 마지막 데이터 다음달부터)
    
    Returns:
        예측 결과 DataFrame
    """
    if start_date is None:
        # 모델의 마지막 날짜 다음달부터 시작
        last_date = model.history['ds'].max()
        if last_date.month == 12:
            start_date = datetime(last_date.year + 1, 1, 1)
        else:
            start_date = datetime(last_date.year, last_date.month + 1, 1)
    
    # 예측 기간 생성
    future_dates = []
    current = start_date
    for _ in range(periods):
        future_dates.append(current)
        if current.month == 12:
            current = datetime(current.year + 1, 1, 1)
        else:
            current = datetime(current.year, current.month + 1, 1)
    
    future = pd.DataFrame({'ds': future_dates})
    forecast = model.predict(future)
    
    return forecast


def analyze_prediction_factors(df: pd.DataFrame, forecast: Dict, is_current_month: bool = False) -> Dict:
    """
    예측 근거 분석 (간단한 통계 기반)
    Prophet은 SHAP과 직접 호환되지 않으므로 통계적 분석 사용
    
    Args:
        df: 과거 데이터 DataFrame
        forecast: 예측 결과
    
    Returns:
        분석 결과 딕셔너리
    """
    factors = {}
    
    # 1. 최근 추세 분석
    recent_months = df.tail(3)
    trend = '상승' if recent_months['avg_price'].iloc[-1] > recent_months['avg_price'].iloc[0] else '하락'
    factors['trend'] = {
        'direction': trend,
        'recent_avg': recent_months['avg_price'].mean(),
        'change_rate': ((recent_months['avg_price'].iloc[-1] - recent_months['avg_price'].iloc[0]) / recent_months['avg_price'].iloc[0]) * 100
    }
    
    # 2. 거래량 변화 분석
    if 'trade_count' in df.columns:
        recent_volume = df.tail(3)['trade_count'].mean()
        overall_volume = df['trade_count'].mean()
        factors['volume'] = {
            'recent_avg': recent_volume,
            'overall_avg': overall_volume,
            'change': ((recent_volume - overall_volume) / overall_volume) * 100 if overall_volume > 0 else 0
        }
    
    # 3. 계절성 패턴 분석 (월별 평균)
    df['month'] = pd.to_datetime(df['year_month'] + '-01').dt.month
    monthly_avg = df.groupby('month')['avg_price'].mean()
    current_month = forecast['date'].month
    factors['seasonality'] = {
        'current_month_avg': monthly_avg[current_month] if current_month in monthly_avg.index else None,
        'monthly_pattern': monthly_avg.to_dict()
    }
    
    # 4. 예측 신뢰도 (과거 데이터 분산 기반)
    price_std = df['avg_price'].std()
    price_mean = df['avg_price'].mean()
    confidence = max(0, min(100, 100 - (price_std / price_mean * 100))) if price_mean > 0 else 50
    factors['confidence'] = confidence
    
    return factors


def generate_astrology_explanation(factors: Dict, predicted_price: float) -> str:
    """
    점성술사 스타일의 예측 근거 설명 생성
    
    Args:
        factors: 분석 결과 딕셔너리
        predicted_price: 예측 가격
    
    Returns:
        점성술사 스타일 설명 문자열
    """
    explanations = []
    
    # 추세 분석
    trend = factors.get('trend', {})
    if trend.get('direction') == '상승':
        explanations.append(f"✨ 최근 3개월간 상승 기운이 감지되었어요. ({trend.get('change_rate', 0):.1f}% 상승)")
    else:
        explanations.append(f"📉 최근 3개월간 하락 흐름이 보여요. ({abs(trend.get('change_rate', 0)):.1f}% 하락)")
    
    # 거래량 분석
    volume = factors.get('volume', {})
    if volume.get('change', 0) > 10:
        explanations.append(f"📊 거래량이 평균보다 {volume.get('change', 0):.1f}% 높아 활발한 시장 움직임이 있어요.")
    elif volume.get('change', 0) < -10:
        explanations.append(f"📊 거래량이 평균보다 {abs(volume.get('change', 0)):.1f}% 낮아 신중한 거래 분위기예요.")
    
    # 계절성 분석
    seasonality = factors.get('seasonality', {})
    current_month_avg = seasonality.get('current_month_avg')
    if current_month_avg:
        if predicted_price > current_month_avg * 1.05:
            explanations.append(f"🌟 이번 달은 평년 같은 달보다 높은 가격대를 보여줄 예정이에요.")
        elif predicted_price < current_month_avg * 0.95:
            explanations.append(f"🌙 이번 달은 평년 같은 달보다 낮은 가격대가 예상돼요.")
    
    # 신뢰도
    confidence = factors.get('confidence', 50)
    if confidence > 70:
        explanations.append(f"🔮 예측 신뢰도가 {confidence:.0f}%로 높은 편이에요.")
    elif confidence < 50:
        explanations.append(f"🔮 예측 신뢰도가 {confidence:.0f}%로 변동성이 큰 시장이에요.")
    
    return "\n".join(explanations)


def save_model(model: Prophet, filepath: str):
    """
    모델을 pickle 파일로 저장
    
    Args:
        model: 학습된 Prophet 모델
        filepath: 저장 경로
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)


def load_model(filepath: str) -> Prophet:
    """
    저장된 모델 로드
    
    Args:
        filepath: 모델 파일 경로
    
    Returns:
        Prophet 모델
    """
    with open(filepath, 'rb') as f:
        model = pickle.load(f)
    return model

