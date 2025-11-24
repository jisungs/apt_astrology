# 🔮 아파트 가격 예측 프로그램 (Apt Astrology)

점성술사 느낌의 아파트 다음달 가격 예측 웹앱

## 📋 프로젝트 개요

주소를 입력하면 해당 아파트의 최근 24개월 실거래가를 분석하여 머신러닝 기반으로 다음달 가격을 예측하고, 예측 근거를 점성술사 스타일로 설명해주는 웹 애플리케이션입니다.

## 🚀 시작하기

### 1. 환경 설정

```bash
# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows

# 패키지 설치
cd backend
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 API 키를 설정하세요:

```bash
cp .env.example .env
# .env 파일을 열어서 API 키 입력
```

필요한 API 키:
- 공공데이터 포털 API 키 (국토교통부 아파트 실거래가 API)

### 3. 데이터 수집 테스트

```bash
cd backend
python test_data_collection.py
```

## 📦 프로젝트 구조

```
apt_astrology/
├── backend/              # 백엔드 코드
│   ├── main.py          # FastAPI 앱 (예정)
│   ├── data_collector.py # 공공데이터 API 연동
│   ├── utils.py         # 유틸리티 함수
│   ├── model.py         # ML 모델 (예정)
│   └── requirements.txt # Python 패키지 의존성
├── frontend/            # 프론트엔드 코드 (예정)
│   ├── templates/       # HTML 템플릿
│   └── static/         # CSS, JS 파일
├── models/              # 학습된 모델 저장
├── data/                # 데이터 파일
│   └── 법정동코드.csv   # 법정동 코드 데이터
└── plans/               # 프로젝트 계획서
```

## 🔧 기술 스택

- **백엔드**: FastAPI
- **ML 모델**: Prophet (시계열 예측)
- **설명 도구**: SHAP
- **시각화**: Plotly + Chart.js
- **프론트엔드**: Jinja2 템플릿

## 📝 진행 상황

- [x] 프로젝트 초기 설정
- [x] 공공데이터 API 기본 연동
- [x] 법정동코드 데이터 준비
- [x] 데이터 수집 모듈 구현
- [ ] 데이터 전처리 파이프라인 완성
- [ ] ML 모델 개발
- [ ] 웹 앱 구현
- [ ] 배포

## 📄 라이선스

MIT License

