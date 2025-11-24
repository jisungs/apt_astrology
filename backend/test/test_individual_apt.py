"""
개별 아파트 예측 테스트 스크립트
"""
import sys
import os

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collector import collect_24months_data, preprocess_trade_data, calculate_monthly_avg_price
from model import (
    prepare_prophet_data,
    train_prophet_model,
    predict_next_month,
    generate_forecast_dataframe,
    analyze_prediction_factors,
    generate_astrology_explanation,
    save_model
)
from visualization import create_price_prediction_chart, create_volume_chart
from utils import format_price
import pandas as pd

if __name__ == "__main__":
    # 테스트할 아파트 정보
    test_address = "서울특별시 종로구"
    test_apt_name = "경희궁자이"  # 개별 아파트명
    
    print("=" * 60)
    print("개별 아파트 가격 예측 테스트")
    print("=" * 60)
    print(f"주소: {test_address}")
    print(f"아파트명: {test_apt_name}\n")
    
    try:
        # 1. 개별 아파트 데이터 수집
        print("1단계: 데이터 수집 중...")
        df_raw = collect_24months_data(test_address, apt_name=test_apt_name)
        
        if len(df_raw) == 0:
            print("\n❌ 해당 아파트의 거래 데이터가 없습니다.")
            exit(1)
        
        # 2. 데이터 전처리
        print("\n2단계: 데이터 전처리 중...")
        df_processed = preprocess_trade_data(df_raw)
        print(f"전처리 완료: {len(df_processed)}건")
        
        # 3. 월별 평균가격 계산
        print("\n3단계: 월별 평균가격 계산 중...")
        df_monthly = calculate_monthly_avg_price(df_processed)
        print(f"월별 평균가격 계산 완료: {len(df_monthly)}개월")
        
        if len(df_monthly) < 12:
            print(f"\n⚠️  경고: 데이터가 {len(df_monthly)}개월뿐입니다. 예측 정확도가 낮을 수 있습니다.")
        
        print("\n월별 평균가격:")
        print(df_monthly.to_string(index=False))
        
        # 4. CSV 저장
        output_path = f"../data/monthly_avg_price_{test_apt_name.replace(' ', '_')}.csv"
        df_monthly.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n데이터 저장 완료: {output_path}")
        
        # 5. Prophet 모델 학습
        print("\n4단계: Prophet 모델 학습 중...")
        df_prophet = prepare_prophet_data(df_monthly)
        model = train_prophet_model(df_prophet)
        print("모델 학습 완료!")
        
        # 6. 이번달과 다음달 예측
        print("\n5단계: 이번달 및 다음달 가격 예측 중...")
        last_date = df_prophet['ds'].max()
        from model import predict_current_and_next_month
        predictions = predict_current_and_next_month(model, last_date)
        
        current_forecast = predictions['current_month']
        next_forecast = predictions['next_month']
        
        print("\n" + "=" * 60)
        print("🔮 예측 결과")
        print("=" * 60)
        print(f"아파트: {test_apt_name}\n")
        
        print("1. 이번달 예측 가격")
        print(f"   예측 날짜: {current_forecast['date'].strftime('%Y년 %m월')}")
        print(f"   예측 가격: {format_price(int(current_forecast['predicted_price']))}")
        print(f"   하한: {format_price(int(current_forecast['lower_bound']))}")
        print(f"   상한: {format_price(int(current_forecast['upper_bound']))}\n")
        
        print("2. 다음달 예측 가격")
        print(f"   예측 날짜: {next_forecast['date'].strftime('%Y년 %m월')}")
        print(f"   예측 가격: {format_price(int(next_forecast['predicted_price']))}")
        print(f"   하한: {format_price(int(next_forecast['lower_bound']))}")
        print(f"   상한: {format_price(int(next_forecast['upper_bound']))}")
        
        # 7. 예측 근거 분석 (다음달 기준)
        print("\n" + "=" * 60)
        print("📊 예측 근거 분석 (다음달 기준)")
        print("=" * 60)
        factors = analyze_prediction_factors(df_monthly, next_forecast)
        print(f"추세: {factors['trend']['direction']} ({factors['trend']['change_rate']:.1f}%)")
        print(f"거래량 변화: {factors['volume']['change']:.1f}%")
        print(f"예측 신뢰도: {factors['confidence']:.1f}%")
        
        # 8. 점성술사 스타일 설명 (다음달 기준)
        print("\n" + "=" * 60)
        print("🔮 점성술사의 예언")
        print("=" * 60)
        explanation = generate_astrology_explanation(factors, next_forecast['predicted_price'])
        print(explanation)
        
        # 9. 향후 6개월 예측
        print("\n" + "=" * 60)
        print("향후 6개월 예측")
        print("=" * 60)
        future_forecast = generate_forecast_dataframe(model, periods=6)
        print(future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_string(index=False))
        
        # 10. 시각화
        print("\n6단계: 시각화 생성 중...")
        price_chart_html = create_price_prediction_chart(
            df_monthly,
            future_forecast,
            next_forecast,  # 다음달 예측 사용
            title=f"{test_apt_name} 가격 예측"
        )
        
        volume_chart_html = create_volume_chart(
            df_monthly,
            title=f"{test_apt_name} 거래량 추이"
        )
        
        # HTML 파일로 저장
        output_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{test_apt_name} 가격 예측</title>
    <style>
        body {{
            background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
            color: #FFD700;
            font-family: 'Arial', sans-serif;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: #FFD700;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
        }}
        .info {{
            background: rgba(0, 0, 0, 0.5);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border: 2px solid #9370DB;
        }}
        .chart-container {{
            background: rgba(0, 0, 0, 0.5);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border: 2px solid #9370DB;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔮 {test_apt_name} 가격 예측</h1>
        
        <div class="info">
            <h2>예측 정보</h2>
            <p><strong>주소:</strong> {test_address}</p>
            <p><strong>아파트명:</strong> {test_apt_name}</p>
            <h3>1. 이번달 예측 가격</h3>
            <p><strong>예측 날짜:</strong> {current_forecast['date'].strftime('%Y년 %m월')}</p>
            <p><strong>예측 가격:</strong> {format_price(int(current_forecast['predicted_price']))}</p>
            <p><strong>하한:</strong> {format_price(int(current_forecast['lower_bound']))}</p>
            <p><strong>상한:</strong> {format_price(int(current_forecast['upper_bound']))}</p>
            <h3>2. 다음달 예측 가격</h3>
            <p><strong>예측 날짜:</strong> {next_forecast['date'].strftime('%Y년 %m월')}</p>
            <p><strong>예측 가격:</strong> {format_price(int(next_forecast['predicted_price']))}</p>
            <p><strong>하한:</strong> {format_price(int(next_forecast['lower_bound']))}</p>
            <p><strong>상한:</strong> {format_price(int(next_forecast['upper_bound']))}</p>
            <p><strong>예측 신뢰도:</strong> {factors['confidence']:.1f}%</p>
        </div>
        
        <div class="chart-container">
            {price_chart_html}
        </div>
        
        <div class="chart-container">
            {volume_chart_html}
        </div>
    </div>
</body>
</html>
"""
        
        viz_output_path = f"../data/visualization_{test_apt_name.replace(' ', '_')}.html"
        with open(viz_output_path, 'w', encoding='utf-8') as f:
            f.write(output_html)
        
        print(f"\n시각화 HTML 저장 완료: {viz_output_path}")
        
        # 11. 모델 저장
        model_path = f"../models/prophet_model_{test_apt_name.replace(' ', '_')}.pkl"
        save_model(model, model_path)
        print(f"모델 저장 완료: {model_path}")
        
        print("\n" + "=" * 60)
        print("✅ 개별 아파트 예측 테스트 완료!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

