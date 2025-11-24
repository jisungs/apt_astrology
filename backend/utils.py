"""
유틸리티 함수 모듈
- 주소 → 법정동 코드 변환
- 날짜 처리 유틸리티
"""
import pandas as pd
import os
from typing import Optional, Tuple


def load_dong_code_data() -> pd.DataFrame:
    """법정동코드 CSV 파일 로드"""
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', '법정동코드.csv')
    df = pd.read_csv(csv_path, encoding='utf-8')
    return df


def address_to_dong_code(address: str) -> Optional[str]:
    """
    주소를 입력받아 법정동 코드를 반환
    
    Args:
        address: 주소 문자열 (예: "서울특별시 종로구 청운동")
    
    Returns:
        법정동 코드 (10자리 문자열) 또는 None
    """
    df = load_dong_code_data()
    
    # 폐지되지 않은 법정동만 필터링
    active_df = df[df['폐지여부'] == '존재']
    
    # 주소에서 법정동명 찾기
    # 간단한 매칭 로직 (향후 개선 가능)
    address_parts = address.split()
    
    for _, row in active_df.iterrows():
        dong_name = row['법정동명']
        # 주소에 법정동명이 포함되어 있는지 확인
        if any(part in dong_name for part in address_parts if len(part) > 1):
            return str(row['법정동코드'])[:10]  # 10자리 코드 반환
    
    return None


def parse_year_month(year_month: str) -> Tuple[int, int]:
    """
    YYYYMM 형식의 문자열을 년도와 월로 파싱
    
    Args:
        year_month: "202411" 형식의 문자열
    
    Returns:
        (년도, 월) 튜플
    """
    year = int(year_month[:4])
    month = int(year_month[4:])
    return year, month


def generate_year_month_list(start_year: int, start_month: int, months: int = 24) -> list:
    """
    시작 년월부터 지정된 개월 수만큼 YYYYMM 형식의 리스트 생성
    
    Args:
        start_year: 시작 년도
        start_month: 시작 월
        months: 생성할 개월 수 (기본값: 24)
    
    Returns:
        YYYYMM 형식의 문자열 리스트
    """
    year_month_list = []
    year = start_year
    month = start_month
    
    for _ in range(months):
        year_month_list.append(f"{year}{month:02d}")
        
        month += 1
        if month > 12:
            month = 1
            year += 1
    
    return year_month_list


def format_price(price: int) -> str:
    """
    가격을 한글 형식으로 포맷팅
    
    Args:
        price: 가격 (원 단위)
    
    Returns:
        포맷팅된 문자열 (예: "7억 2,300만원")
    """
    if price >= 100000000:
        eok = price // 100000000
        manwon = (price % 100000000) // 10000
        if manwon > 0:
            return f"{eok}억 {manwon:,}만원"
        else:
            return f"{eok}억원"
    elif price >= 10000:
        manwon = price // 10000
        return f"{manwon:,}만원"
    else:
        return f"{price:,}원"

