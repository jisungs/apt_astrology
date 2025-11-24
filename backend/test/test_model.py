"""
ML 모델 테스트 스크립트
- 전체 지역 데이터 또는 개별 아파트 데이터로 테스트 가능
"""
import sys
import os

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from model import (
    prepare_prophet_data,
    train_prophet_model,
    predict_next_month,
    predict_current_and_next_month,
    generate_forecast_dataframe,
    analyze_prediction_factors,
    generate_astrology_explanation,
    save_model
)
from utils import format_price

if __name__ == "__main__":
    # 사용법: python test_model.py [아파트명]
    # 예: python test_model.py 경희궁자이
    apt_name = sys.argv[1] if len(sys.argv) > 1 else None
    
    print("=" * 50)
    print("Prophet 모델 테스트")
    print("=" * 50)
    
    if apt_name:
        print(f"개별 아파트 모드: {apt_name}")
        csv_path = f"../data/monthly_avg_price_{apt_name.replace(' ', '_')}.csv"
    else:
        print("전체 지역 모드")
        csv_path = "../data/monthly_avg_price.csv"
    
    # 데이터 로드
    df = pd.read_csv(csv_path)
    print(f"\n데이터 로드 완료: {len(df)}개월")
    print(df.head())
    
    # Prophet 형식으로 변환
    df_prophet = prepare_prophet_data(df)
    print(f"\nProphet 데이터 준비 완료:")
    print(df_prophet.head())
    
    # 모델 학습
    print("\n모델 학습 중...")
    model = train_prophet_model(df_prophet)
    print("모델 학습 완료!")
    
    # 이번달과 다음달 예측
    last_date = df_prophet['ds'].max()
    predictions = predict_current_and_next_month(model, last_date)
    
    current_forecast = predictions['current_month']
    next_forecast = predictions['next_month']
    
    print("\n" + "=" * 50)
    print("가격 예측 결과")
    print("=" * 50)
    
    print("\n1. 이번달 예측 가격")
    print(f"   예측 날짜: {current_forecast['date'].strftime('%Y년 %m월')}")
    print(f"   예측 가격: {format_price(int(current_forecast['predicted_price']))}")
    print(f"   하한: {format_price(int(current_forecast['lower_bound']))}")
    print(f"   상한: {format_price(int(current_forecast['upper_bound']))}")
    
    print("\n2. 다음달 예측 가격")
    print(f"   예측 날짜: {next_forecast['date'].strftime('%Y년 %m월')}")
    print(f"   예측 가격: {format_price(int(next_forecast['predicted_price']))}")
    print(f"   하한: {format_price(int(next_forecast['lower_bound']))}")
    print(f"   상한: {format_price(int(next_forecast['upper_bound']))}")
    
    # 예측 근거 분석 (다음달 기준)
    print("\n" + "=" * 50)
    print("예측 근거 분석 (다음달 기준)")
    print("=" * 50)
    factors = analyze_prediction_factors(df, next_forecast)
    print(f"추세: {factors['trend']['direction']} ({factors['trend']['change_rate']:.1f}%)")
    print(f"거래량 변화: {factors['volume']['change']:.1f}%")
    print(f"예측 신뢰도: {factors['confidence']:.1f}%")
    
    # 점성술사 스타일 설명 (다음달 기준)
    print("\n" + "=" * 50)
    print("🔮 점성술사의 예언")
    print("=" * 50)
    explanation = generate_astrology_explanation(factors, next_forecast['predicted_price'])
    print(explanation)
    
    # 향후 6개월 예측
    print("\n" + "=" * 50)
    print("향후 6개월 예측")
    print("=" * 50)
    future_forecast = generate_forecast_dataframe(model, periods=6)
    print(future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_string(index=False))
    
    # 모델 저장
    model_path = "../models/prophet_model.pkl"
    save_model(model, model_path)
    print(f"\n모델 저장 완료: {model_path}")

