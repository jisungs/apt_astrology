"""
시각화 모듈
- Plotly 인터랙티브 그래프 생성 (애니메이션 강화)
- 점성술사 컨셉 스타일 적용
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Optional
import json


def create_price_prediction_chart(
    historical_data: pd.DataFrame,
    forecast_data: pd.DataFrame,
    next_month_prediction: Dict,
    title: str = "아파트 가격 예측",
    include_plotlyjs: bool = True,
    div_id: Optional[str] = None
) -> str:
    """
    가격 예측 그래프 생성 (Plotly, 애니메이션 강화)
    
    Args:
        historical_data: 과거 데이터 DataFrame (year_month, avg_price)
        forecast_data: 예측 데이터 DataFrame (Prophet forecast)
        next_month_prediction: 다음달 예측 결과 딕셔너리
        title: 그래프 제목
    
    Returns:
        Plotly 그래프를 HTML 문자열로 변환한 결과
    """
    # 과거 데이터 준비
    historical_data = historical_data.copy()
    historical_data['date'] = pd.to_datetime(historical_data['year_month'] + '-01')
    
    # 그래프 생성
    fig = go.Figure()
    
    # 과거 데이터 라인 (애니메이션 효과)
    fig.add_trace(go.Scatter(
        x=historical_data['date'],
        y=historical_data['avg_price'],
        mode='lines+markers',
        name='과거 가격',
        line=dict(
            color='#9370DB',  # 보라색 (점성술사 컨셉)
            width=3,
            shape='spline'  # 부드러운 곡선
        ),
        marker=dict(
            size=8,
            color='#FFD700',  # 금색 마커
            line=dict(width=2, color='#9370DB')
        ),
        hovertemplate='<b>%{x|%Y년 %m월}</b><br>' +
                      '가격: %{y:,.0f}원<extra></extra>'
    ))
    
    # 예측 구간 (신뢰구간)
    fig.add_trace(go.Scatter(
        x=forecast_data['ds'],
        y=forecast_data['yhat_upper'],
        mode='lines',
        name='상한선',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast_data['ds'],
        y=forecast_data['yhat_lower'],
        mode='lines',
        name='신뢰구간',
        fill='tonexty',
        fillcolor='rgba(147, 112, 219, 0.2)',  # 반투명 보라색
        line=dict(width=0),
        hovertemplate='<b>%{x|%Y년 %m월}</b><br>' +
                      '하한: %{y:,.0f}원<extra></extra>'
    ))
    
    # 예측 라인
    fig.add_trace(go.Scatter(
        x=forecast_data['ds'],
        y=forecast_data['yhat'],
        mode='lines+markers',
        name='예측 가격',
        line=dict(
            color='#FFD700',  # 금색
            width=3,
            dash='dash',  # 점선
            shape='spline'
        ),
        marker=dict(
            size=10,
            color='#FFD700',
            symbol='star',  # 별 모양
            line=dict(width=2, color='#9370DB')
        ),
        hovertemplate='<b>%{x|%Y년 %m월}</b><br>' +
                      '예측: %{y:,.0f}원<extra></extra>'
    ))
    
    # 다음달 예측점 강조 (빛나는 효과)
    next_date = next_month_prediction['date']
    next_price = next_month_prediction['predicted_price']
    
    fig.add_trace(go.Scatter(
        x=[next_date],
        y=[next_price],
        mode='markers+text',
        name='다음달 예측',
        marker=dict(
            size=20,
            color='#FFD700',
            symbol='star',
            line=dict(width=3, color='#9370DB'),
            # 빛나는 효과를 위한 여러 레이어
        ),
        text=['✨'],
        textposition='middle center',
        textfont=dict(size=20),
        hovertemplate='<b>%{x|%Y년 %m월}</b><br>' +
                      f'예측 가격: {next_price:,.0f}원<extra></extra>'
    ))
    
    # 레이아웃 설정 (점성술사 컨셉)
    fig.update_layout(
        title=dict(
            text=f'🔮 {title}',
            font=dict(size=24, color='#FFD700'),
            x=0.5
        ),
        xaxis=dict(
            title=dict(text='날짜', font=dict(color='#9370DB')),
            tickfont=dict(color='#9370DB'),
            gridcolor='rgba(147, 112, 219, 0.2)'
        ),
        yaxis=dict(
            title=dict(text='가격 (원)', font=dict(color='#9370DB')),
            tickfont=dict(color='#9370DB'),
            gridcolor='rgba(147, 112, 219, 0.2)',
            tickformat=',.0f'
        ),
        plot_bgcolor='rgba(0, 0, 0, 0)',  # 투명 배경
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(family='Arial, sans-serif', color='#9370DB'),
        legend=dict(
            bgcolor='rgba(0, 0, 0, 0.7)',
            bordercolor='#9370DB',
            borderwidth=1,
            font=dict(color='#FFD700')
        ),
        hovermode='x unified',
        # 애니메이션 설정
        transition=dict(duration=500, easing='cubic-in-out'),
        # 어두운 테마
        template='plotly_dark',
        height=600
    )
    
    # 고유한 div_id 생성 (제공되지 않은 경우)
    if div_id is None:
        import uuid
        div_id = f'price-chart-{uuid.uuid4().hex[:8]}'
    
    # HTML로 변환
    html_str = fig.to_html(
        include_plotlyjs='cdn' if include_plotlyjs else False,
        div_id=div_id,
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'price_prediction',
                'height': 600,
                'width': 1200,
                'scale': 2
            }
        }
    )
    
    return html_str


def create_volume_chart(
    historical_data: pd.DataFrame,
    title: str = "거래량 추이",
    include_plotlyjs: bool = False,
    div_id: Optional[str] = None
) -> str:
    """
    거래량 추이 차트 생성
    
    Args:
        historical_data: 과거 데이터 DataFrame (year_month, trade_count)
        title: 그래프 제목
    
    Returns:
        Plotly 그래프를 HTML 문자열로 변환한 결과
    """
    historical_data = historical_data.copy()
    historical_data['date'] = pd.to_datetime(historical_data['year_month'] + '-01')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=historical_data['date'],
        y=historical_data['trade_count'],
        name='거래량',
        marker=dict(
            color=historical_data['trade_count'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title=dict(text='거래량', font=dict(color='#FFD700')))
        ),
        hovertemplate='<b>%{x|%Y년 %m월}</b><br>' +
                      '거래량: %{y}건<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f'📊 {title}',
            font=dict(size=20, color='#FFD700'),
            x=0.5
        ),
        xaxis=dict(
            title=dict(text='날짜', font=dict(color='#9370DB')),
            tickfont=dict(color='#9370DB')
        ),
        yaxis=dict(
            title=dict(text='거래량 (건)', font=dict(color='#9370DB')),
            tickfont=dict(color='#9370DB')
        ),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(family='Arial, sans-serif', color='#9370DB'),
        template='plotly_dark',
        height=400
    )
    
    # 고유한 div_id 생성 (제공되지 않은 경우)
    if div_id is None:
        import uuid
        div_id = f'volume-chart-{uuid.uuid4().hex[:8]}'
    
    html_str = fig.to_html(
        include_plotlyjs='cdn' if include_plotlyjs else False,
        div_id=div_id,
        config={'displayModeBar': False}
    )
    
    return html_str


def format_price_for_display(price: float) -> str:
    """
    가격을 한글 형식으로 포맷팅 (그래프용)
    
    Args:
        price: 가격 (원 단위)
    
    Returns:
        포맷팅된 문자열
    """
    if price >= 100000000:
        eok = price // 100000000
        manwon = (price % 100000000) // 10000
        if manwon > 0:
            return f"{int(eok)}억 {int(manwon):,}만원"
        else:
            return f"{int(eok)}억원"
    elif price >= 10000:
        manwon = price // 10000
        return f"{int(manwon):,}만원"
    else:
        return f"{int(price):,}원"

