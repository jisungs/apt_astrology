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
from utils import address_to_dong_code, generate_year_month_list, parse_year_month

load_dotenv()

PUBLIC_API_KEY = os.getenv("PUBLIC_API_KEY")
API_URL = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"


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
        print(f"XML 파싱 오류: {e}")
        return []


def fetch_apt_trade_data(lawd_cd: str, deal_ymd: str) -> List[Dict]:
    """
    특정 법정동 코드와 거래월의 아파트 실거래가 데이터 조회
    
    Args:
        lawd_cd: 법정동 코드 (10자리)
        deal_ymd: 거래년월 (YYYYMM 형식)
    
    Returns:
        거래 데이터 딕셔너리 리스트
    """
    params = {
        "serviceKey": PUBLIC_API_KEY,
        "pageNo": 1,
        "numOfRows": 1000,
        "LAWD_CD": lawd_cd,
        "DEAL_YMD": deal_ymd,
    }
    
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        # XML 파싱
        data = parse_xml_response(response.text)
        return data
    except requests.exceptions.RequestException as e:
        print(f"API 요청 오류 ({deal_ymd}): {e}")
        return []
    except Exception as e:
        print(f"데이터 수집 오류 ({deal_ymd}): {e}")
        return []


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
    
    print(f"법정동 코드: {lawd_cd}")
    
    # 최근 24개월 년월 리스트 생성
    from datetime import datetime
    now = datetime.now()
    year_month_list = generate_year_month_list(
        now.year - 2, now.month, 24
    )
    
    # 역순으로 정렬 (최신 데이터부터)
    year_month_list.reverse()
    
    all_data = []
    
    print(f"총 {len(year_month_list)}개월 데이터 수집 시작...")
    for i, deal_ymd in enumerate(year_month_list, 1):
        print(f"[{i}/{len(year_month_list)}] {deal_ymd} 데이터 수집 중...")
        data = fetch_apt_trade_data(lawd_cd, deal_ymd)
        
        if data:
            all_data.extend(data)
            print(f"  → {len(data)}건 수집 완료")
        else:
            print(f"  → 데이터 없음")
        
        # API 호출 제한을 고려한 딜레이 (필요시)
        import time
        time.sleep(0.1)
    
    if not all_data:
        raise ValueError("수집된 데이터가 없습니다.")
    
    # DataFrame 생성
    df = pd.DataFrame(all_data)
    
    # 아파트명 필터링 (선택사항)
    if apt_name and '아파트' in df.columns:
        df = df[df['아파트'].str.contains(apt_name, na=False)]
    
    print(f"\n총 {len(df)}건의 거래 데이터 수집 완료")
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
    # 필요한 컬럼만 선택 및 정리
    columns_mapping = {
        '년': 'year',
        '월': 'month',
        '거래금액': 'price',
        '전용면적': 'area',
        '층': 'floor',
        '건축년도': 'build_year',
        '아파트': 'apt_name',
        '법정동': 'dong',
    }
    
    # 존재하는 컬럼만 매핑
    available_columns = {k: v for k, v in columns_mapping.items() if k in df.columns}
    df_processed = df[list(available_columns.keys())].copy()
    df_processed = df_processed.rename(columns=available_columns)
    
    # 데이터 타입 변환
    if 'price' in df_processed.columns:
        # 거래금액에서 쉼표 제거 후 숫자로 변환
        df_processed['price'] = df_processed['price'].str.replace(',', '').astype(float)
    
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
        df_processed['year_month'] = df_processed['year'].astype(str) + '-' + df_processed['month'].astype(str).str.zfill(2)
    
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

