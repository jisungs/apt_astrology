"""
공공데이터 API 연동 모듈
- 국토교통부 아파트 실거래가 API 호출
- 최근 24개월 데이터 수집
"""
import os
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from dotenv import load_dotenv
import logging

from utils import address_to_dong_code, generate_year_month_list, parse_year_month

logger = logging.getLogger(__name__)

load_dotenv()

PUBLIC_API_KEY = os.getenv("PUBLIC_API_KEY")
API_URL = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"

# API 키 검증
if not PUBLIC_API_KEY or PUBLIC_API_KEY.strip() == "":
    logger.warning("PUBLIC_API_KEY가 설정되지 않았습니다. 환경 변수를 확인하세요.")
else:
    logger.info("API 키가 설정되었습니다.")


def parse_xml_response(xml_text: str) -> List[Dict]:
    """
    XML 응답을 파싱하여 딕셔너리 리스트로 변환
    
    Args:
        xml_text: XML 형식의 응답 텍스트
    
    Returns:
        거래 데이터 딕셔너리 리스트
    """
    try:
        root = ET.fromstring(xml_text)
        items = []
        
        for item in root.findall('.//item'):
            item_dict = {}
            for child in item:
                item_dict[child.tag] = child.text
            items.append(item_dict)
        
        return items
    except ET.ParseError as e:
        logger.error(f"XML 파싱 오류: {e}")
        return []


def fetch_apt_trade_data(lawd_cd: str, deal_ymd: str) -> List[Dict]:
    """
    특정 법정동 코드와 거래월의 아파트 실거래가 데이터 조회
    
    Args:
        lawd_cd: 법정동 코드 (10자리 또는 5자리)
        deal_ymd: 거래년월 (YYYYMM 형식)
    
    Returns:
        거래 데이터 딕셔너리 리스트
    """
    # API는 5자리 코드(구 단위)를 사용하므로 변환
    # 10자리 코드인 경우 앞 5자리만 사용
    if len(lawd_cd) == 10:
        lawd_cd = lawd_cd[:5]
    
    params = {
        "serviceKey": PUBLIC_API_KEY,
        "pageNo": 1,
        "numOfRows": 1000,
        "LAWD_CD": lawd_cd,
        "DEAL_YMD": deal_ymd,
    }
    
    try:
        # API 키 검증
        if not PUBLIC_API_KEY or PUBLIC_API_KEY.strip() == "":
            logger.error("API 키가 설정되지 않았습니다")
            return []
        
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        # XML 파싱
        data = parse_xml_response(response.text)
        logger.debug(f"API 데이터 수집 성공 - 법정동코드: {lawd_cd}, 거래월: {deal_ymd}, 건수: {len(data)}")
        return data
    except requests.exceptions.RequestException as e:
        logger.warning(f"API 요청 오류 ({deal_ymd}): {e}")
        return []
    except Exception as e:
        logger.error(f"데이터 수집 오류 ({deal_ymd}): {e}", exc_info=True)
        return []


def get_apartment_list(address: str, months: int = 3, use_cache: bool = True) -> List[str]:
    """
    특정 주소의 아파트 목록 조회 (CSV 캐시 사용)
    
    Args:
        address: 주소 문자열
        months: 조회할 개월 수 (기본값: 3개월, 캐시 사용 시 무시됨)
        use_cache: CSV 캐시 사용 여부 (기본값: True)
    
    Returns:
        아파트명 리스트 (중복 제거, 정렬)
    """
    import os
    from pathlib import Path
    
    # CSV 캐시 파일 경로 생성
    cache_dir = Path(__file__).parent.parent / "data" / "apartment_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # 주소를 파일명으로 사용 (특수문자 제거)
    safe_address = address.replace(" ", "_").replace("/", "_")
    cache_file = cache_dir / f"apartments_{safe_address}.csv"
    
    # 캐시에서 읽기 시도
    if use_cache and cache_file.exists():
        try:
            df_cache = pd.read_csv(cache_file, encoding='utf-8')
            if 'apartment_name' in df_cache.columns:
                apartment_list = df_cache['apartment_name'].dropna().unique().tolist()
                apartment_list = sorted([apt for apt in apartment_list if apt and apt.strip()])
                logger.info(f"캐시에서 아파트 목록 로드: {len(apartment_list)}개 (주소: {address})")
                return apartment_list
        except Exception as e:
            logger.warning(f"캐시 파일 읽기 오류: {e}, API에서 새로 수집합니다.")
    
    # 캐시가 없거나 읽기 실패 시 API에서 수집
    logger.info(f"API에서 아파트 목록 수집 중... (주소: {address})")
    
    # 주소 → 법정동 코드 변환
    lawd_cd = address_to_dong_code(address)
    if not lawd_cd:
        return []
    
    # 최근 N개월 년월 리스트 생성
    from datetime import datetime
    now = datetime.now()
    year_month_list = generate_year_month_list(now.year - 1, now.month, months)
    year_month_list.reverse()  # 최신 데이터부터
    
    apartment_set = set()
    
    logger.info(f"아파트 목록 수집 중... (최근 {months}개월)")
    for i, deal_ymd in enumerate(year_month_list[:months], 1):
        logger.debug(f"[{i}/{min(months, len(year_month_list))}] {deal_ymd} 데이터 조회 중...")
        data = fetch_apt_trade_data(lawd_cd, deal_ymd)
        
        for item in data:
            if 'aptNm' in item and item['aptNm']:
                apt_name = item['aptNm'].strip()
                if apt_name and apt_name != ' ':
                    apartment_set.add(apt_name)
        
        import time
        time.sleep(0.1)  # API 호출 제한 고려
    
    apartment_list = sorted(list(apartment_set))
    logger.info(f"총 {len(apartment_list)}개의 아파트를 찾았습니다.")
    
    # CSV 캐시에 저장
    if apartment_list:
        try:
            df_cache = pd.DataFrame({'apartment_name': apartment_list})
            df_cache.to_csv(cache_file, index=False, encoding='utf-8')
            logger.info(f"아파트 목록 캐시 저장 완료: {cache_file}")
        except Exception as e:
            logger.warning(f"캐시 파일 저장 오류: {e}")
    
    return apartment_list


def collect_24months_data(address: str, apt_name: Optional[str] = None) -> pd.DataFrame:
    """
    주소를 입력받아 최근 24개월 아파트 실거래가 데이터 수집
    
    Args:
        address: 주소 문자열
        apt_name: 아파트명 (선택사항, 필터링용)
    
    Returns:
        거래 데이터가 담긴 DataFrame
    """
    # 주소 → 법정동 코드 변환
    lawd_cd = address_to_dong_code(address)
    if not lawd_cd:
        raise ValueError(f"주소를 법정동 코드로 변환할 수 없습니다: {address}")
    
    logger.info(f"법정동 코드: {lawd_cd}")
    
    # 최근 24개월 년월 리스트 생성
    from datetime import datetime
    now = datetime.now()
    year_month_list = generate_year_month_list(
        now.year - 2, now.month, 24
    )
    
    # 역순으로 정렬 (최신 데이터부터)
    year_month_list.reverse()
    
    all_data = []
    
    logger.info(f"총 {len(year_month_list)}개월 데이터 수집 시작...")
    for i, deal_ymd in enumerate(year_month_list, 1):
        logger.debug(f"[{i}/{len(year_month_list)}] {deal_ymd} 데이터 수집 중...")
        data = fetch_apt_trade_data(lawd_cd, deal_ymd)
        
        if data:
            all_data.extend(data)
            logger.debug(f"  → {len(data)}건 수집 완료")
        else:
            logger.debug(f"  → 데이터 없음")
        
        # API 호출 제한을 고려한 딜레이 (필요시)
        import time
        time.sleep(0.1)
    
    if not all_data:
        raise ValueError("수집된 데이터가 없습니다.")
    
    # DataFrame 생성
    df = pd.DataFrame(all_data)
    
    # 아파트명 필터링 (선택사항)
    if apt_name:
        if 'aptNm' in df.columns:
            # 부분 일치 검색 (대소문자 구분 없음)
            df_filtered = df[df['aptNm'].str.contains(apt_name, case=False, na=False)]
            if len(df_filtered) == 0:
                logger.warning(f"'{apt_name}'와 일치하는 아파트를 찾을 수 없습니다. 사용 가능한 아파트명 샘플: {df['aptNm'].unique()[:5].tolist()}")
            else:
                df = df_filtered
                logger.info(f"'{apt_name}' 아파트 필터링 완료: {len(df)}건")
        else:
            logger.warning("아파트명 컬럼을 찾을 수 없습니다.")
    
    logger.info(f"총 {len(df)}건의 거래 데이터 수집 완료")
    return df


def preprocess_trade_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    거래 데이터 전처리
    - 컬럼명 정리
    - 데이터 타입 변환
    - 월별 평균가격 계산 준비
    
    Args:
        df: 원본 거래 데이터 DataFrame
    
    Returns:
        전처리된 DataFrame
    """
    # XML 응답의 실제 컬럼명에 맞춘 매핑
    columns_mapping = {
        'dealYear': 'year',
        'dealMonth': 'month',
        'dealAmount': 'price',
        'excluUseAr': 'area',
        'floor': 'floor',
        'buildYear': 'build_year',
        'aptNm': 'apt_name',
        'umdNm': 'dong',
    }
    
    # 존재하는 컬럼만 매핑
    available_columns = {k: v for k, v in columns_mapping.items() if k in df.columns}
    df_processed = df[list(available_columns.keys())].copy()
    df_processed = df_processed.rename(columns=available_columns)
    
    # 데이터 타입 변환
    if 'price' in df_processed.columns:
        # 거래금액에서 쉼표 제거 후 숫자로 변환 (만원 단위)
        df_processed['price'] = df_processed['price'].str.replace(',', '').astype(float) * 10000
    
    if 'area' in df_processed.columns:
        df_processed['area'] = pd.to_numeric(df_processed['area'], errors='coerce')
    
    if 'floor' in df_processed.columns:
        df_processed['floor'] = pd.to_numeric(df_processed['floor'], errors='coerce')
    
    if 'build_year' in df_processed.columns:
        df_processed['build_year'] = pd.to_numeric(df_processed['build_year'], errors='coerce')
    
    if 'year' in df_processed.columns:
        df_processed['year'] = pd.to_numeric(df_processed['year'], errors='coerce')
    
    if 'month' in df_processed.columns:
        df_processed['month'] = pd.to_numeric(df_processed['month'], errors='coerce')
    
    # 년월 컬럼 생성 (시계열 분석용)
    if 'year' in df_processed.columns and 'month' in df_processed.columns:
        df_processed['year_month'] = df_processed['year'].astype(int).astype(str) + '-' + df_processed['month'].astype(int).astype(str).str.zfill(2)
    
    return df_processed


def calculate_monthly_avg_price(df: pd.DataFrame) -> pd.DataFrame:
    """
    월별 평균 거래가격 계산
    
    Args:
        df: 전처리된 거래 데이터 DataFrame
    
    Returns:
        월별 평균가격 DataFrame (year_month, avg_price 컬럼 포함)
    """
    if 'price' not in df.columns or 'year_month' not in df.columns:
        raise ValueError("필요한 컬럼이 없습니다. (price, year_month)")
    
    monthly_avg = df.groupby('year_month')['price'].agg(['mean', 'count']).reset_index()
    monthly_avg.columns = ['year_month', 'avg_price', 'trade_count']
    
    # 정렬 (오래된 순서부터)
    monthly_avg = monthly_avg.sort_values('year_month').reset_index(drop=True)
    
    return monthly_avg
