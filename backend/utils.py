"""
유틸리티 함수 모듈
- 주소 → 법정동 코드 변환
- 날짜 처리 유틸리티
"""
import pandas as pd
import os
from typing import Optional, Tuple, List, Dict


def load_dong_code_data() -> pd.DataFrame:
    """법정동코드 CSV 파일 로드"""
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', '법정동코드.csv')
    df = pd.read_csv(csv_path, encoding='utf-8')
    return df


def normalize_address(address: str) -> str:
    """
    주소를 정규화 (사용자 입력을 표준 형식으로 변환)
    
    Args:
        address: 사용자 입력 주소
    
    Returns:
        정규화된 주소
    """
    # 공백 제거 및 정리
    address = address.strip()
    
    # 시/도 정규화 매핑
    city_mapping = {
        '부산': '부산광역시',
        '서울': '서울특별시',
        '대구': '대구광역시',
        '인천': '인천광역시',
        '광주': '광주광역시',
        '대전': '대전광역시',
        '울산': '울산광역시',
        '세종': '세종특별자치시',
        '경기': '경기도',
        '강원': '강원도',
        '충북': '충청북도',
        '충남': '충청남도',
        '전북': '전라북도',
        '전남': '전라남도',
        '경북': '경상북도',
        '경남': '경상남도',
        '제주': '제주특별자치도',
    }
    
    # 주소 시작 부분 확인 및 변환
    for key, value in city_mapping.items():
        if address.startswith(key) and not address.startswith(value):
            # "부산 해운대구" -> "부산광역시 해운대구"
            address = address.replace(key, value, 1)
            break
    
    return address


def address_to_dong_code(address: str) -> Optional[str]:
    """
    주소를 입력받아 법정동 코드를 반환
    
    Args:
        address: 주소 문자열 (예: "서울특별시 종로구" 또는 "부산 해운대구")
    
    Returns:
        법정동 코드 (10자리 문자열) 또는 None
    """
    # 주소 정규화
    normalized_address = normalize_address(address)
    
    df = load_dong_code_data()
    
    # 먼저 존재하는 법정동에서 찾기
    active_df = df[df['폐지여부'] == '존재'].copy()
    
    # 정확한 매칭 우선 (가장 구체적인 주소부터)
    active_df['name_length'] = active_df['법정동명'].str.len()
    active_df = active_df.sort_values('name_length', ascending=False)
    
    # 정규화된 주소로 정확히 일치하는 경우
    exact_match = active_df[active_df['법정동명'] == normalized_address]
    if not exact_match.empty:
        return str(exact_match.iloc[0]['법정동코드'])[:10]
    
    # 정규화된 주소가 법정동명에 포함되는 경우
    for _, row in active_df.iterrows():
        dong_name = row['법정동명']
        if normalized_address in dong_name:
            code = str(row['법정동코드'])[:10]
            # 시/도 전체 코드는 제외하고, 구 단위 이상만 반환
            if code not in ['1100000000', '2600000000', '2700000000', '2800000000', 
                           '2900000000', '3000000000', '3100000000', '3600000000']:
                return code
    
    # 존재하는 법정동에서 못 찾으면 폐지된 법정동도 확인 (부산 등)
    # 폐지된 법정동은 "부산직할시" -> "부산광역시"로 매핑 필요
    all_df = df.copy()
    all_df['name_length'] = all_df['법정동명'].str.len()
    all_df = all_df.sort_values('name_length', ascending=False)
    
    # 폐지된 법정동명을 현재 형식으로 변환하여 매칭
    for _, row in all_df.iterrows():
        dong_name = row['법정동명']
        # "부산직할시" -> "부산광역시" 변환
        converted_name = dong_name.replace('직할시', '광역시')
        if normalized_address in converted_name or converted_name.startswith(normalized_address):
            code = str(row['법정동코드'])[:10]
            # 시/도 전체 코드 제외, 구 단위 이상만 반환
            if len(code) == 10 and not code.endswith('00000000'):
                return code
    
    return None


def get_city_list() -> List[Dict[str, str]]:
    """
    시/도 목록 조회
    
    Returns:
        시/도 목록 (코드, 이름)
    """
    df = load_dong_code_data()
    
    # 시/도 단위만 추출 (코드가 00으로 끝나는 것)
    cities = df[df['법정동코드'].astype(str).str.endswith('00000000')].copy()
    cities = cities[cities['폐지여부'] == '존재']
    
    # 정규화된 이름으로 변환
    city_list = []
    for _, row in cities.iterrows():
        city_name = row['법정동명']
        # "부산직할시" -> "부산광역시" 변환
        city_name = city_name.replace('직할시', '광역시')
        city_list.append({
            'code': str(row['법정동코드'])[:2],
            'name': city_name
        })
    
    return sorted(city_list, key=lambda x: x['name'])


def get_district_list(city_code: str) -> List[Dict[str, str]]:
    """
    시/도 코드에 해당하는 구/군 목록 조회
    
    Args:
        city_code: 시/도 코드 (2자리)
    
    Returns:
        구/군 목록 (코드, 이름)
    """
    df = load_dong_code_data()
    
    # 해당 시/도의 구/군 단위 추출 (코드가 00으로 끝나는 것, 시/도 코드로 시작)
    districts = df[
        (df['법정동코드'].astype(str).str.startswith(city_code)) &
        (df['법정동코드'].astype(str).str.endswith('00000')) &
        (~df['법정동코드'].astype(str).str.endswith('00000000'))
    ].copy()
    
    # 존재하는 것만 필터링
    districts = districts[districts['폐지여부'] == '존재']
    
    district_list = []
    for _, row in districts.iterrows():
        district_name = row['법정동명']
        # "부산직할시 해운대구" -> "부산광역시 해운대구" -> "해운대구"
        district_name = district_name.replace('직할시', '광역시')
        # 시/도명 제거하고 구/군명만 추출
        parts = district_name.split()
        if len(parts) >= 2:
            district_name = ' '.join(parts[1:])  # 시/도명 제외
        district_list.append({
            'code': str(row['법정동코드'])[:5],
            'name': district_name
        })
    
    # 중복 제거 및 정렬
    seen = set()
    unique_districts = []
    for d in district_list:
        if d['name'] not in seen:
            seen.add(d['name'])
            unique_districts.append(d)
    
    return sorted(unique_districts, key=lambda x: x['name'])


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
