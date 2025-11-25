"""
FastAPI 웹 애플리케이션
점성술사 느낌의 아파트 가격 예측 웹앱
"""
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import pandas as pd
from typing import Optional
import logging

# 로깅 설정
import logging_config
logger = logging.getLogger(__name__)

# 커스텀 예외 및 스키마
from exceptions import PredictionError, DataCollectionError, ModelTrainingError, ValidationError
from schemas import PredictionRequest

# 데이터 수집 및 모델
from data_collector import collect_24months_data, preprocess_trade_data, calculate_monthly_avg_price, get_apartment_list
from model import (
    prepare_prophet_data,
    train_prophet_model,
    predict_current_and_next_month,
    analyze_prediction_factors,
    generate_astrology_explanation,
    load_model,
    save_model
)
from visualization import create_price_prediction_chart, create_volume_chart
from utils import format_price, get_city_list, get_district_list

app = FastAPI(title="🔮 아파트 가격 예측", description="점성술사 느낌의 아파트 가격 예측 서비스")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        # 배포 시 실제 도메인 추가 필요
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Rate Limiting 설정
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info("Rate Limiting 활성화됨")
except ImportError:
    logger.warning("slowapi가 설치되지 않아 Rate Limiting이 비활성화됩니다. pip install slowapi로 설치하세요.")
    limiter = None

# 정적 파일 및 템플릿 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "frontend", "templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/predict", response_class=HTMLResponse)
async def predict(
    request: Request,
    address: str = Form(...),
    apt_name: Optional[str] = Form(None)
):
    """
    가격 예측 API
    
    Args:
        address: 주소 (예: "서울특별시 종로구")
        apt_name: 아파트명 (선택사항)
    """
    
    try:
        # 입력 검증
        try:
            validated_request = PredictionRequest(address=address, apt_name=apt_name)
            address = validated_request.address
            apt_name = validated_request.apt_name
        except Exception as e:
            logger.warning(f"입력 검증 실패: {str(e)}")
            raise ValidationError(f"입력 검증 실패: {str(e)}")
        
        # 1. 데이터 수집
        logger.info(f"예측 요청 - 주소: {address}, 아파트명: {apt_name or '전체'}")
        try:
            df_raw = collect_24months_data(address, apt_name=apt_name)
        except Exception as e:
            logger.error(f"데이터 수집 실패: {str(e)}", exc_info=True)
            raise DataCollectionError(f"데이터 수집 중 오류가 발생했습니다: {str(e)}")
        
        if len(df_raw) == 0:
            logger.warning(f"데이터 없음 - 주소: {address}")
            raise DataCollectionError(f"'{address}' 지역의 거래 데이터를 찾을 수 없습니다.")
        
        # 2. 데이터 전처리
        df_processed = preprocess_trade_data(df_raw)
        df_monthly = calculate_monthly_avg_price(df_processed)
        
        # 마지막 실거래 정보 추출
        last_trade = None
        if len(df_processed) > 0:
            # 년월과 거래일 기준으로 정렬하여 가장 최근 거래 찾기
            df_sorted = df_processed.sort_values(
                by=['year', 'month'], 
                ascending=False
            ).reset_index(drop=True)
            
            # 가장 최근 거래 (첫 번째 행)
            latest = df_sorted.iloc[0]
            
            # 데이터 포맷팅 (템플릿에서 사용하기 쉽도록)
            year_val = int(latest.get('year', 0)) if pd.notna(latest.get('year')) else 0
            month_val = int(latest.get('month', 0)) if pd.notna(latest.get('month')) else 0
            price_val = int(latest.get('price', 0)) if pd.notna(latest.get('price')) else 0
            
            last_trade = {
                'date': f"{year_val}년 {month_val}월",
                'year_month': latest.get('year_month', ''),
                'price': price_val,
                'price_formatted': format_price(price_val),
            }
            
            # 면적 (있으면 포맷팅)
            if pd.notna(latest.get('area')):
                area_val = float(latest.get('area'))
                last_trade['area'] = f"{area_val:.2f}"
            
            # 층수 (있으면 정수로 변환)
            if pd.notna(latest.get('floor')):
                floor_val = int(float(latest.get('floor')))
                last_trade['floor'] = f"{floor_val}"
            
            # 건축년도 (있으면 정수로 변환)
            if pd.notna(latest.get('build_year')):
                build_year_val = int(float(latest.get('build_year')))
                last_trade['build_year'] = f"{build_year_val}"
            
            # 아파트명
            if pd.notna(latest.get('apt_name')):
                last_trade['apt_name'] = str(latest.get('apt_name'))
            elif apt_name:
                last_trade['apt_name'] = apt_name
            
            # 법정동
            if pd.notna(latest.get('dong')):
                last_trade['dong'] = str(latest.get('dong'))
        
        # 데이터 부족 경고 (최소 2개월은 필요하지만, 12개월 미만이면 경고만 표시)
        data_warning = None
        if len(df_monthly) < 2:
            raise HTTPException(
                status_code=400,
                detail=f"데이터가 너무 부족합니다 ({len(df_monthly)}개월). 최소 2개월 이상의 데이터가 필요합니다."
            )
        elif len(df_monthly) < 12:
            data_warning = f"⚠️ 데이터가 {len(df_monthly)}개월로 부족합니다. 예측 정확도가 낮을 수 있습니다. (권장: 12개월 이상)"
            logger.warning(data_warning)
        
        # 3. 모델 학습 또는 로드
        model_key = f"{address}_{apt_name or '전체'}"
        MODELS_DIR = os.path.join(BASE_DIR, "models")
        os.makedirs(MODELS_DIR, exist_ok=True)
        model_path = os.path.join(MODELS_DIR, f"prophet_model_{model_key.replace(' ', '_').replace('/', '_')}.pkl")
        
        if os.path.exists(model_path):
            logger.info(f"기존 모델 로드: {model_path}")
            try:
                model = load_model(model_path)
            except Exception as e:
                logger.error(f"모델 로드 실패: {str(e)}", exc_info=True)
                raise ModelTrainingError(f"모델 로드 중 오류가 발생했습니다: {str(e)}")
        else:
            logger.info("새 모델 학습 중...")
            try:
                df_prophet = prepare_prophet_data(df_monthly)
                model = train_prophet_model(df_prophet)
                save_model(model, model_path)
                logger.info(f"모델 학습 완료 및 저장: {model_path}")
            except Exception as e:
                logger.error(f"모델 학습 실패: {str(e)}", exc_info=True)
                raise ModelTrainingError(f"모델 학습 중 오류가 발생했습니다: {str(e)}")
        
        # 4. 예측 수행
        try:
            df_prophet = prepare_prophet_data(df_monthly)
            last_date = df_prophet['ds'].max()
            predictions = predict_current_and_next_month(model, last_date)
        except Exception as e:
            logger.error(f"예측 수행 실패: {str(e)}", exc_info=True)
            raise PredictionError(f"예측 수행 중 오류가 발생했습니다: {str(e)}")
        
        current_forecast = predictions['current_month']
        next_forecast = predictions['next_month']
        
        # 4-1. 예측 가격을 마지막 실거래 가격 기준으로 조정 (차이가 30% 이상일 때만 5%~15% 범위에서 랜덤 조정)
        if last_trade and 'price' in last_trade:
            import random
            last_price = last_trade['price']
            threshold_ratio = 0.30  # 30% 이상 차이일 때 조정
            min_adjustment = 0.05  # 최소 5%
            max_adjustment = 0.15  # 최대 15%
            
            # 현재달 예측 가격 조정
            predicted_current = current_forecast['predicted_price']
            price_diff_ratio = abs(predicted_current - last_price) / last_price if last_price > 0 else 0
            
            # 차이가 30% 이상일 때만 조정
            if price_diff_ratio >= threshold_ratio:
                # 5%~15% 범위에서 랜덤하게 조정 비율 선택
                random_adjustment = random.uniform(min_adjustment, max_adjustment)
                
                # 예측 가격의 변화 방향을 유지하되, 랜덤 조정 범위 내로 제한
                if predicted_current < last_price:
                    # 하락 예측인 경우, 마지막 거래가 기준 -5%~-15% 범위로 조정
                    adjusted_current = last_price * (1 - random_adjustment)
                else:
                    # 상승 예측인 경우, 마지막 거래가 기준 +5%~+15% 범위로 조정
                    adjusted_current = last_price * (1 + random_adjustment)
                
                # 예측 가격과의 차이 비율 계산
                diff_ratio = (adjusted_current - predicted_current) / predicted_current if predicted_current != 0 else 0
                
                # 하한/상한도 동일한 비율로 조정
                current_forecast['predicted_price'] = adjusted_current
                current_forecast['lower_bound'] = current_forecast['lower_bound'] * (1 + diff_ratio)
                current_forecast['upper_bound'] = current_forecast['upper_bound'] * (1 + diff_ratio)
                
                adjustment_percent = random_adjustment * 100
                logger.info(f"가격 조정 - 현재달 예측: {predicted_current:,.0f}원 → {adjusted_current:,.0f}원 (차이: {price_diff_ratio*100:.1f}%, 마지막 거래가: {last_price:,.0f}원 기준 ±{adjustment_percent:.1f}% 랜덤 조정)")
            
            # 다음달 예측 가격 조정
            predicted_next = next_forecast['predicted_price']
            price_diff_ratio_next = abs(predicted_next - last_price) / last_price if last_price > 0 else 0
            
            # 차이가 30% 이상일 때만 조정
            if price_diff_ratio_next >= threshold_ratio:
                # 5%~15% 범위에서 랜덤하게 조정 비율 선택 (현재달과 독립적으로)
                random_adjustment_next = random.uniform(min_adjustment, max_adjustment)
                
                if predicted_next < last_price:
                    # 하락 예측인 경우, 마지막 거래가 기준 -5%~-15% 범위로 조정
                    adjusted_next = last_price * (1 - random_adjustment_next)
                else:
                    # 상승 예측인 경우, 마지막 거래가 기준 +5%~+15% 범위로 조정
                    adjusted_next = last_price * (1 + random_adjustment_next)
                
                diff_ratio = (adjusted_next - predicted_next) / predicted_next if predicted_next != 0 else 0
                
                next_forecast['predicted_price'] = adjusted_next
                next_forecast['lower_bound'] = next_forecast['lower_bound'] * (1 + diff_ratio)
                next_forecast['upper_bound'] = next_forecast['upper_bound'] * (1 + diff_ratio)
                
                adjustment_percent_next = random_adjustment_next * 100
                logger.info(f"가격 조정 - 다음달 예측: {predicted_next:,.0f}원 → {adjusted_next:,.0f}원 (차이: {price_diff_ratio_next*100:.1f}%, 마지막 거래가: {last_price:,.0f}원 기준 ±{adjustment_percent_next:.1f}% 랜덤 조정)")
        
        # 5. 예측 근거 분석
        last_price_for_analysis = last_trade['price'] if last_trade and 'price' in last_trade else None
        factors = analyze_prediction_factors(df_monthly, next_forecast, last_trade_price=last_price_for_analysis)
        explanation = generate_astrology_explanation(factors, next_forecast['predicted_price'], last_trade_price=last_price_for_analysis)
        
        # 6. 향후 6개월 예측 (그래프용)
        from model import generate_forecast_dataframe
        future_forecast = generate_forecast_dataframe(model, periods=6)
        
        # 7. 시각화 생성
        # 첫 번째 그래프만 Plotly.js 포함, 두 번째는 제외하여 중복 로드 방지
        price_chart_html = create_price_prediction_chart(
            df_monthly,
            future_forecast,
            next_forecast,
            title=f"{apt_name or address} 가격 예측",
            include_plotlyjs=True,  # 첫 번째 그래프만 Plotly.js 포함
            div_id='price-chart-main'
        )
        
        volume_chart_html = create_volume_chart(
            df_monthly,
            title=f"{apt_name or address} 거래량 추이",
            include_plotlyjs=False,  # 두 번째 그래프는 Plotly.js 제외
            div_id='volume-chart-main'
        )
        
        # 8. 결과 페이지 렌더링
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "address": address,
                "apt_name": apt_name,
                "current_forecast": current_forecast,
                "next_forecast": next_forecast,
                "factors": factors,
                "explanation": explanation,
                "price_chart_html": price_chart_html,
                "volume_chart_html": volume_chart_html,
                "format_price": format_price,
                "data_warning": data_warning,
                "data_months": len(df_monthly),
                "last_trade": last_trade,
            }
        )
        
    except (HTTPException, PredictionError, DataCollectionError, ModelTrainingError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"예측 중 예상치 못한 오류 발생: {str(e)}", exc_info=True)
        raise PredictionError(f"예측 중 오류가 발생했습니다: {str(e)}")


@app.get("/api/cities")
async def get_cities():
    """시/도 목록 조회 API"""
    try:
        cities = get_city_list()
        logger.info(f"시/도 목록 조회 성공: {len(cities)}개")
        return {
            "success": True,
            "cities": cities
        }
    except Exception as e:
        logger.error(f"시/도 목록 조회 실패: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "cities": []
        }


@app.get("/api/districts")
async def get_districts(city_code: str):
    """
    시/도 코드에 해당하는 구/군 목록 조회 API
    
    Args:
        city_code: 시/도 코드 (2자리)
    """
    try:
        districts = get_district_list(city_code)
        logger.info(f"구/군 목록 조회 성공 - 시/도 코드: {city_code}, {len(districts)}개")
        return {
            "success": True,
            "city_code": city_code,
            "districts": districts
        }
    except Exception as e:
        logger.error(f"구/군 목록 조회 실패 - 시/도 코드: {city_code}, 오류: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "districts": []
        }


@app.get("/api/apartments")
async def get_apartments(address: str):
    """
    주소에 해당하는 아파트 목록 조회 API
    
    Args:
        address: 주소 문자열
    
    Returns:
        아파트명 리스트
    """
    try:
        apartment_list = get_apartment_list(address, months=3)
        logger.info(f"아파트 목록 조회 성공 - 주소: {address}, {len(apartment_list)}개")
        return {
            "success": True,
            "address": address,
            "apartments": apartment_list,
            "count": len(apartment_list)
        }
    except Exception as e:
        logger.error(f"아파트 목록 조회 실패 - 주소: {address}, 오류: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "apartments": []
        }


@app.get("/explain", response_class=HTMLResponse)
async def explain(request: Request):
    """예측 근거 설명 페이지"""
    return templates.TemplateResponse("explanation.html", {"request": request})


@app.get("/health")
async def health():
    """헬스 체크"""
    return {"status": "ok", "message": "🔮 점성술사의 예언 서비스가 정상 작동 중입니다."}


if __name__ == "__main__":
    import uvicorn
    logger.info("=" * 60)
    logger.info("🔮 점성술사의 아파트 가격 예측 서비스 시작")
    logger.info("=" * 60)
    logger.info("서버 주소: http://localhost:8000")
    logger.info("API 문서: http://localhost:8000/docs")
    logger.info("=" * 60)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

