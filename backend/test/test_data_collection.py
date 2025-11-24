"""
데이터 수집 테스트 스크립트
"""
import sys
import os

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collector import collect_24months_data, preprocess_trade_data, calculate_monthly_avg_price
import pandas as pd

if __name__ == "__main__":
    # 테스트 주소 (서울시 종로구)
    test_address = "서울특별시 종로구"
    # test_apt_name = None  # 전체 데이터 수집
    # test_apt_name = "경희궁자이"  # 개별 아파트 수집 (주석 해제하여 사용)
    test_apt_name = None
    
    print("=" * 50)
    print("아파트 실거래가 데이터 수집 테스트")
    print("=" * 50)
    print(f"주소: {test_address}")
    if test_apt_name:
        print(f"아파트명: {test_apt_name} (개별 아파트 모드)")
    else:
        print("아파트명: 없음 (전체 데이터 모드)")
    print()
    
    try:
        # 24개월 데이터 수집
        df_raw = collect_24months_data(test_address, apt_name=test_apt_name)
        
        # 데이터 전처리
        df_processed = preprocess_trade_data(df_raw)
        print(f"\n전처리 완료: {len(df_processed)}건")
        
        # 월별 평균가격 계산
        df_monthly = calculate_monthly_avg_price(df_processed)
        print(f"\n월별 평균가격 계산 완료: {len(df_monthly)}개월")
        print("\n월별 평균가격:")
        print(df_monthly.to_string(index=False))
        
        # CSV 저장
        output_path = "../data/monthly_avg_price.csv"
        df_monthly.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n데이터 저장 완료: {output_path}")
        
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()

