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

**중요**: `.env` 파일은 프로젝트 루트 디렉토리에 있어야 합니다.

### 3. 데이터 수집 테스트

```bash
cd backend

# 전체 지역 데이터 수집 (종로구 전체)
python test/test_data_collection.py

# 개별 아파트 데이터 수집
python test/test_individual_apt.py  # 경희궁자이 예시

# 모델 테스트
python test/test_model.py

# 시각화 테스트
python test/test_visualization.py
```

### 4. 웹 서버 실행

#### ⭐ 방법 1: uvicorn 명령어로 실행 (권장)

```bash
# 프로젝트 루트에서 실행
cd /Users/jisungs/Documents/dev/sideprojects/apt_astrology

# 가상환경 활성화
source venv/bin/activate

# 웹 서버 시작
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**실행 예시:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

서버가 시작되면:
- 🌐 **메인 페이지**: http://localhost:8000
- 📚 **API 문서**: http://localhost:8000/docs
- ❤️ **헬스 체크**: http://localhost:8000/health

#### 방법 2: Python으로 직접 실행

```bash
cd backend
source ../venv/bin/activate
python main.py
```

**주의**: 이 방법은 `reload` 모드가 제대로 작동하지 않을 수 있습니다. 
경고 메시지가 나오면 방법 1을 사용하세요.

#### 방법 3: 프로덕션 모드 실행

```bash
cd backend
source ../venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 실행 위치 중요사항

⚠️ **중요**: 웹 서버는 반드시 `backend` 디렉토리에서 실행해야 합니다!

```bash
# 올바른 실행 방법
cd backend                    # backend 디렉토리로 이동
source ../venv/bin/activate   # 가상환경 활성화
uvicorn main:app --reload     # 서버 실행

# 잘못된 실행 방법 (프로젝트 루트에서 실행)
cd /Users/jisungs/Documents/dev/sideprojects/apt_astrology
uvicorn backend.main:app --reload  # 이렇게 하면 경로 문제 발생 가능
```

### 5. 웹 앱 사용 방법

1. 브라우저에서 http://localhost:8000 접속
2. 주소 입력 (예: "서울특별시 종로구")
3. 아파트명 입력 (선택사항, 예: "경희궁자이")
4. "예지력으로 가격 예측하기" 버튼 클릭
5. 예측 결과 확인:
   - 이번달 예측 가격
   - 다음달 예측 가격
   - 점성술사 스타일 설명
   - 인터랙티브 그래프
   - 예측 근거 분석

### 6. 문제 해결

#### ⚠️ "You must pass the application as an import string" 경고 해결

이 경고는 `python main.py`로 실행할 때 `reload=True` 옵션 때문에 발생합니다.

**해결 방법:**
```bash
# 방법 1: uvicorn 명령어 사용 (권장)
cd backend
uvicorn main:app --reload

# 방법 2: main.py에서 reload 제거
# main.py의 마지막 줄을 다음과 같이 수정:
# uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

#### 서버가 시작되지 않는 경우
- 가상환경이 활성화되어 있는지 확인: `which python` (venv 경로여야 함)
- 필요한 패키지가 설치되어 있는지 확인: `pip install -r requirements.txt`
- 포트 8000이 이미 사용 중인지 확인: `lsof -i :8000`
- **backend 디렉토리에서 실행하고 있는지 확인**

#### 템플릿/정적 파일을 찾을 수 없는 경우
- `backend` 디렉토리에서 실행해야 합니다
- `frontend/templates/`와 `frontend/static/` 폴더가 프로젝트 루트에 있는지 확인

#### 데이터 수집 오류가 발생하는 경우
- `.env` 파일에 API 키가 올바르게 설정되어 있는지 확인
- 공공데이터 포털 API 호출 제한 확인 (일일 호출 제한이 있을 수 있음)
- API 키가 프로젝트 루트의 `.env` 파일에 있는지 확인

#### 모델 학습 오류가 발생하는 경우
- 최소 12개월 이상의 데이터가 필요합니다
- 데이터가 부족한 경우 다른 지역으로 테스트해보세요

#### 예측 요청 시 오류가 발생하는 경우
- 브라우저 콘솔에서 오류 메시지 확인
- 서버 터미널에서 상세 오류 로그 확인
- API 키가 올바르게 설정되어 있는지 확인

## 📦 프로젝트 구조

```
apt_astrology/
├── backend/              # 백엔드 코드
│   ├── main.py          # FastAPI 앱
│   ├── data_collector.py # 공공데이터 API 연동
│   ├── model.py         # ML 모델
│   ├── visualization.py  # 시각화 모듈
│   ├── utils.py         # 유틸리티 함수
│   ├── requirements.txt # Python 패키지 의존성
│   └── test/            # 테스트 스크립트
│       ├── test_data_collection.py
│       ├── test_model.py
│       ├── test_visualization.py
│       └── test_individual_apt.py
├── frontend/            # 프론트엔드 코드
│   ├── templates/       # HTML 템플릿
│   │   ├── index.html   # 메인 페이지
│   │   ├── result.html  # 결과 페이지
│   │   └── explanation.html # 근거 설명 페이지
│   └── static/         # CSS, JS 파일
│       ├── style.css    # 점성술사 컨셉 스타일
│       ├── script.js    # 클라이언트 로직
│       └── chart-config.js # Chart.js 설정
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
- [x] 데이터 전처리 파이프라인 완성
- [x] ML 모델 개발 (Prophet)
- [x] 개별 아파트 예측 기능 추가
- [x] 시각화 모듈 구현 (Plotly)
- [x] 웹 앱 구현 (FastAPI)
- [ ] 배포

## 🎯 주요 기능

### 1. 전체 지역 예측
- 특정 지역(구 단위)의 모든 아파트 평균 가격 예측
- 예: "서울특별시 종로구" 전체 평균 가격

### 2. 개별 아파트 예측 ⭐
- 특정 아파트만 필터링하여 예측
- 예: "서울특별시 종로구" + "경희궁자이"
- 더 정확한 개별 아파트 가격 예측 가능

## 📄 라이선스

MIT License


