"""
시각화 테스트 스크립트
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
    generate_forecast_dataframe,
    load_model
)
from visualization import create_price_prediction_chart, create_volume_chart

if __name__ == "__main__":
    print("=" * 50)
    print("시각화 테스트")
    print("=" * 50)
    
    # 데이터 로드
    df = pd.read_csv("../data/monthly_avg_price.csv")
    print(f"\n데이터 로드 완료: {len(df)}개월")
    
    # 모델 로드 또는 학습
    model_path = "../models/prophet_model.pkl"
    if os.path.exists(model_path):
        print("\n기존 모델 로드 중...")
        model = load_model(model_path)
    else:
        print("\n모델 학습 중...")
        df_prophet = prepare_prophet_data(df)
        model = train_prophet_model(df_prophet)
    
    # 예측 수행
    df_prophet = prepare_prophet_data(df)
    last_date = df_prophet['ds'].max()
    forecast = predict_next_month(model, last_date)
    future_forecast = generate_forecast_dataframe(model, periods=6)
    
    print("\n그래프 생성 중...")
    
    # 가격 예측 그래프 생성
    price_chart_html = create_price_prediction_chart(
        df,
        future_forecast,
        forecast,
        title="서울 종로구 아파트 가격 예측"
    )
    
    # 거래량 차트 생성
    volume_chart_html = create_volume_chart(
        df,
        title="서울 종로구 거래량 추이"
    )
    
    # HTML 파일로 저장
    output_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>아파트 가격 예측 시각화</title>
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
        <h1>🔮 점성술사의 아파트 가격 예측</h1>
        
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
    
    output_path = "../data/visualization_test.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_html)
    
    print(f"\n시각화 HTML 저장 완료: {output_path}")
    print("브라우저에서 열어서 확인하세요!")

