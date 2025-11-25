# 🚂 Railway 배포 계획서

**작성일**: 2025년 11월 25일  
**배포 플랫폼**: Railway  
**목표**: 서울특별시 서초구 특정 아파트만 선택 가능한 제한된 버전 배포  
**브랜치**: `railway-deployment` (배포 전용 브랜치)

---

## 🌿 Git 브랜치 관리

### 원격 저장소 정보
- **원격 저장소**: `origin` → `https://github.com/jisungs/apt_astrology.git`
- **기본 브랜치**: `main` (원격: `origin/main`)
- **개발 브랜치**: `master` (로컬)
- **배포 브랜치**: `railway-deployment` (로컬, 원격 푸시 필요)

### 브랜치 전략
- **main**: 메인 브랜치 (원격 저장소 기본 브랜치)
- **master**: 개발 버전 (전체 기능 포함, 로컬)
- **railway-deployment**: 배포 버전 (서초구 제한 버전, 원격 푸시 필요)

### 브랜치 작업 흐름
```bash
# 1. 배포 브랜치 생성 및 전환
git checkout -b railway-deployment

# 2. 배포 관련 변경사항 커밋
git add .
git commit -m "feat: Railway 배포용 서초구 제한 버전 구현"

# 3. 원격 저장소에 배포 브랜치 푸시
git push origin railway-deployment

# 4. Railway에서 railway-deployment 브랜치 연결
# Railway 대시보드 → Settings → Source → Branch: railway-deployment 선택
```

### 원격 저장소 연결 확인
```bash
# 원격 저장소 확인
git remote -v

# 원격 브랜치 확인
git branch -r

# 로컬 브랜치 확인
git branch
```

### 배포 브랜치에서만 적용되는 변경사항
- UI 제한 (서초구만 선택 가능)
- API 제한 (서초구 및 지정된 아파트만)
- 모델 파일 매핑 (기존 모델만 사용)

---

## 📋 배포 요구사항

### 1. 지역 제한
- **서울특별시 서초구**만 선택 가능하도록 제한

### 2. 아파트 제한
서초구에서 다음 5개 아파트만 선택 가능:
1. **대림서초시리온** (모델: `prophet_model_서울특별시_서초구_대림서초리시온.pkl`)
2. **디에이치반포클라스** (모델: `prophet_model_서울특별시_서초구_디에이치반포라클라스.pkl`)
3. **래미안_리더스원** (모델: `prophet_model_서울특별시_서초구_래미안_리더스원.pkl`)
4. **롯데캐슬갤럭시** (모델: `prophet_model_서울특별시_서초구_롯데캐슬갤럭시.pkl`)
5. **대우아이빌** (모델: `prophet_model_서울특별시_서초구_대우아이빌.pkl`)

### 3. 모델 활용
- `models/` 폴더에 있는 학습된 모델 파일들을 활용
- 모델 학습 없이 기존 모델만 사용

---

## 🎯 구현 계획

### Phase 1: UI 제한 구현

#### 1.1 시/도 드롭다운 제한
**파일**: `frontend/static/script.js`

**작업 내용**:
- 시/도 드롭다운에서 "서울특별시"만 표시
- 다른 시/도는 선택 불가능하도록 설정

**구현 방법**:
```javascript
async function loadCityList() {
    const citySelect = document.getElementById('city');
    
    // 서초구 배포 버전: 서울특별시만 표시
    citySelect.innerHTML = '<option value="">시/도 선택</option>';
    const option = document.createElement('option');
    option.value = '11'; // 서울특별시 코드
    option.textContent = '서울특별시';
    citySelect.appendChild(option);
    
    // 서울특별시 자동 선택 (선택사항)
    citySelect.value = '11';
    await loadDistrictList('11');
}
```

#### 1.2 구/군 드롭다운 제한
**파일**: `frontend/static/script.js`

**작업 내용**:
- 구/군 드롭다운에서 "서초구"만 표시
- 다른 구/군은 선택 불가능하도록 설정

**구현 방법**:
```javascript
async function loadDistrictList(cityCode) {
    const districtSelect = document.getElementById('district');
    
    // 서초구 배포 버전: 서초구만 표시
    districtSelect.innerHTML = '<option value="">구/군 선택</option>';
    const option = document.createElement('option');
    option.value = '11650'; // 서초구 코드
    option.textContent = '서초구';
    districtSelect.appendChild(option);
    
    // 서초구 자동 선택
    districtSelect.value = '11650';
    const addressInput = document.getElementById('address');
    addressInput.value = '서울특별시 서초구';
    
    // 아파트 목록 로드
    await loadApartmentList('서울특별시 서초구');
}
```

#### 1.3 아파트 드롭다운 제한
**파일**: `frontend/static/script.js`

**작업 내용**:
- 아파트 드롭다운에서 지정된 5개 아파트만 표시
- 다른 아파트는 표시하지 않음

**구현 방법**:
```javascript
async function loadApartmentList(address) {
    const aptSelect = document.getElementById('apt_name');
    const loadingIndicator = document.getElementById('loading_apt');
    
    aptSelect.disabled = true;
    loadingIndicator.style.display = 'block';
    
    // 서초구 배포 버전: 지정된 5개 아파트만 표시
    const allowedApartments = [
        { name: '대림서초시리온', value: '대림서초리시온' },
        { name: '디에이치반포클라스', value: '디에이치반포라클라스' },
        { name: '래미안 리더스원', value: '래미안_리더스원' },
        { name: '롯데캐슬갤럭시', value: '롯데캐슬갤럭시' },
        { name: '대우아이빌', value: '대우아이빌' }
    ];
    
    loadingIndicator.style.display = 'none';
    aptSelect.innerHTML = '<option value="">아파트 선택</option>';
    
    allowedApartments.forEach(apt => {
        const option = document.createElement('option');
        option.value = apt.value; // 모델 파일명과 일치하는 값
        option.textContent = apt.name; // 사용자에게 보여줄 이름
        aptSelect.appendChild(option);
    });
    
    aptSelect.disabled = false;
}
```

---

### Phase 2: 백엔드 제한 구현

#### 2.1 API 엔드포인트 제한
**파일**: `backend/main.py`

**작업 내용**:
- `/api/cities` 엔드포인트: 서울특별시만 반환
- `/api/districts` 엔드포인트: 서초구만 반환
- `/api/apartments` 엔드포인트: 지정된 5개 아파트만 반환

**구현 방법**:
```python
@app.get("/api/cities")
async def get_cities():
    """시/도 목록 조회 API (서초구 배포 버전: 서울특별시만)"""
    try:
        # 서초구 배포 버전: 서울특별시만 반환
        cities = [{"code": "11", "name": "서울특별시"}]
        logger.info(f"시/도 목록 조회 성공: {len(cities)}개 (제한된 버전)")
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
    """구/군 목록 조회 API (서초구 배포 버전: 서초구만)"""
    try:
        # 서초구 배포 버전: 서초구만 반환
        districts = [{"code": "11650", "name": "서초구"}]
        logger.info(f"구/군 목록 조회 성공 - 시/도 코드: {city_code}, {len(districts)}개 (제한된 버전)")
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
    """아파트 목록 조회 API (서초구 배포 버전: 지정된 5개만)"""
    try:
        # 서초구 배포 버전: 지정된 5개 아파트만 반환
        allowed_apartments = [
            {"name": "대림서초시리온", "value": "대림서초리시온"},
            {"name": "디에이치반포클라스", "value": "디에이치반포라클라스"},
            {"name": "래미안 리더스원", "value": "래미안_리더스원"},
            {"name": "롯데캐슬갤럭시", "value": "롯데캐슬갤럭시"},
            {"name": "대우아이빌", "value": "대우아이빌"}
        ]
        
        logger.info(f"아파트 목록 조회 성공 - 주소: {address}, {len(allowed_apartments)}개 (제한된 버전)")
        return {
            "success": True,
            "address": address,
            "apartments": [apt["value"] for apt in allowed_apartments],
            "count": len(allowed_apartments)
        }
    except Exception as e:
        logger.error(f"아파트 목록 조회 실패 - 주소: {address}, 오류: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "apartments": []
        }
```

#### 2.2 예측 엔드포인트 검증
**파일**: `backend/main.py`

**작업 내용**:
- `/predict` 엔드포인트에서 주소와 아파트명 검증
- 서초구가 아니거나 지정된 아파트가 아니면 에러 반환

**구현 방법**:
```python
@app.post("/predict", response_class=HTMLResponse)
async def predict(
    request: Request,
    address: str = Form(...),
    apt_name: Optional[str] = Form(None)
):
    """
    가격 예측 API (서초구 배포 버전)
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
        
        # 서초구 배포 버전: 주소 검증
        if "서초구" not in address:
            logger.warning(f"허용되지 않은 주소: {address}")
            raise ValidationError("서초구 배포 버전에서는 서울특별시 서초구만 선택할 수 있습니다.")
        
        # 서초구 배포 버전: 아파트명 검증
        allowed_apartments = ["대림서초리시온", "디에이치반포라클라스", "래미안_리더스원", "롯데캐슬갤럭시", "대우아이빌"]
        if apt_name and apt_name not in allowed_apartments:
            logger.warning(f"허용되지 않은 아파트: {apt_name}")
            raise ValidationError(f"서초구 배포 버전에서는 다음 아파트만 선택할 수 있습니다: {', '.join(allowed_apartments)}")
        
        # ... 기존 예측 로직 ...
```

---

### Phase 3: 모델 파일 활용

#### 3.1 모델 파일 매핑
**파일**: `backend/main.py`

**작업 내용**:
- 아파트명을 모델 파일명으로 매핑
- 모델 파일이 존재하면 로드, 없으면 에러 반환

**구현 방법**:
```python
# 모델 파일명 매핑 (아파트명 -> 모델 파일명)
MODEL_FILE_MAPPING = {
    "대림서초리시온": "prophet_model_서울특별시_서초구_대림서초리시온.pkl",
    "디에이치반포라클라스": "prophet_model_서울특별시_서초구_디에이치반포라클라스.pkl",
    "래미안_리더스원": "prophet_model_서울특별시_서초구_래미안_리더스원.pkl",
    "롯데캐슬갤럭시": "prophet_model_서울특별시_서초구_롯데캐슬갤럭시.pkl",
    "대우아이빌": "prophet_model_서울특별시_서초구_대우아이빌.pkl"
}

# 예측 엔드포인트에서 모델 로드
if apt_name and apt_name in MODEL_FILE_MAPPING:
    model_filename = MODEL_FILE_MAPPING[apt_name]
    model_path = os.path.join(MODELS_DIR, model_filename)
    
    if os.path.exists(model_path):
        logger.info(f"기존 모델 로드: {model_path}")
        model = load_model(model_path)
    else:
        logger.error(f"모델 파일을 찾을 수 없습니다: {model_path}")
        raise ModelTrainingError(f"모델 파일을 찾을 수 없습니다: {model_filename}")
else:
    # 아파트명이 없거나 매핑에 없는 경우 에러
    raise ValidationError("지정된 아파트를 선택해주세요.")
```

#### 3.2 모델 파일 배포
**작업 내용**:
- `models/` 폴더의 모델 파일들을 Railway에 배포
- `.gitignore`에서 `models/*.pkl` 제외 확인

**주의사항**:
- 모델 파일 크기가 크므로 Git LFS 사용 고려
- 또는 Railway의 파일 시스템에 직접 업로드

---

### Phase 4: Railway 배포 설정

#### 4.1 Procfile 생성
**파일**: `Procfile` (프로젝트 루트)

**내용**:
```
web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 4.2 runtime.txt 생성 (제거됨)
**⚠️ 중요**: `runtime.txt` 파일은 Railway 배포 시 오류를 발생시킵니다.

**문제점**:
- Railway가 `runtime.txt`를 발견하면 `mise`를 사용하여 Python을 설치하려고 시도
- `mise`가 Python 3.11.0의 precompiled 버전을 찾지 못해 빌드 실패
- 에러: `mise ERROR no precompiled python found for core:python@3.11.0`

**해결 방법**:
- `runtime.txt` 파일을 **제거**해야 합니다
- Railway는 `requirements.txt`를 분석하여 Python 버전을 자동으로 감지합니다
- Python 버전을 명시적으로 지정하려면 `nixpacks.toml` 파일을 사용하세요

#### 4.3 railway.json 생성 (선택사항)
**파일**: `railway.json` (프로젝트 루트)

**내용**:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r backend/requirements.txt"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 4.4 원격 저장소 연결
**현재 상태**:
- **원격 저장소**: `origin` → `https://github.com/jisungs/apt_astrology.git`
- **기본 브랜치**: `main` (원격: `origin/main`)
- **배포 브랜치**: `railway-deployment` (로컬, 원격 푸시 필요)

**배포 브랜치 푸시**:
```bash
# 배포 브랜치로 전환
git checkout railway-deployment

# 원격 저장소에 푸시 (최초)
git push -u origin railway-deployment

# 이후 업데이트
git push origin railway-deployment
```

#### 4.5 Railway와 GitHub 연결
**Railway 대시보드에서 설정**:

1. **프로젝트 생성**: Railway 대시보드에서 새 프로젝트 생성
2. **GitHub 저장소 연결**:
   - "Deploy from GitHub repo" 선택
   - 저장소: `jisungs/apt_astrology` 선택
   - 인증: GitHub OAuth 승인
3. **배포 브랜치 선택**:
   - Settings → Source → Branch
   - `railway-deployment` 선택
4. **자동 배포 활성화**:
   - `railway-deployment` 브랜치에 푸시하면 자동 배포
   - Railway가 GitHub 웹훅을 통해 변경사항 감지

#### 4.6 환경 변수 설정
**Railway 대시보드에서 설정**:

1. **PUBLIC_API_KEY**: 공공데이터 포털 API 키
   - Variables 탭에서 추가
   - Key: `PUBLIC_API_KEY`
   - Value: 실제 API 키 값
2. **PORT**: Railway가 자동으로 설정 (사용자 설정 불필요)

---

### Phase 5: 배포 전 체크리스트

#### 5.1 코드 수정
- [ ] `frontend/static/script.js` - UI 제한 구현
- [ ] `backend/main.py` - API 제한 및 모델 매핑 구현
- [ ] 모델 파일명과 아파트명 매핑 확인

#### 5.2 배포 파일 생성
- [x] `Procfile` 생성 완료
- [x] `runtime.txt` 제거 완료 (Railway 오류 방지)
- [ ] `nixpacks.toml` 생성 (선택사항, Python 버전 명시적 지정 시)

#### 5.3 모델 파일 확인
- [ ] `models/` 폴더에 5개 모델 파일 존재 확인
- [ ] 모델 파일명과 코드의 매핑 일치 확인
- [ ] `.gitignore`에서 모델 파일 제외 확인 (필요시)

#### 5.4 로컬 테스트
- [ ] 서버 실행 테스트
- [ ] UI에서 서초구만 표시되는지 확인
- [ ] 아파트 목록에 5개만 표시되는지 확인
- [ ] 각 아파트 예측 테스트
- [ ] 모델 로드 테스트

#### 5.5 Railway 배포
- [ ] Railway 계정 생성 및 프로젝트 생성
- [ ] GitHub 저장소 연결
- [ ] 환경 변수 설정 (PUBLIC_API_KEY)
- [ ] 배포 실행
- [ ] 배포 후 테스트

---

## 📁 파일 구조

### 수정할 파일
```
apt_astrology/
├── backend/
│   └── main.py                    # API 제한 및 모델 매핑 추가
├── frontend/
│   └── static/
│       └── script.js              # UI 제한 구현
└── models/                        # 모델 파일 (배포 포함)
    ├── prophet_model_서울특별시_서초구_대림서초리시온.pkl
    ├── prophet_model_서울특별시_서초구_디에이치반포라클라스.pkl
    ├── prophet_model_서울특별시_서초구_래미안_리더스원.pkl
    ├── prophet_model_서울특별시_서초구_롯데캐슬갤럭시.pkl
    └── prophet_model_서울특별시_서초구_대우아이빌.pkl
```

### 신규 생성 파일
```
apt_astrology/
├── Procfile                       # Railway 시작 명령
└── nixpacks.toml                  # Railway 설정 (선택사항, Python 버전 명시 시)
```

**⚠️ 중요**: `runtime.txt` 파일은 Railway 배포 시 오류를 발생시키므로 **제거**되었습니다.

---

## 🔧 구현 상세

### 1. 아파트명 매핑 테이블

| 사용자 표시명 | 모델 파일명 | API 값 |
|--------------|------------|--------|
| 대림서초시리온 | prophet_model_서울특별시_서초구_대림서초리시온.pkl | 대림서초리시온 |
| 디에이치반포클라스 | prophet_model_서울특별시_서초구_디에이치반포라클라스.pkl | 디에이치반포라클라스 |
| 래미안 리더스원 | prophet_model_서울특별시_서초구_래미안_리더스원.pkl | 래미안_리더스원 |
| 롯데캐슬갤럭시 | prophet_model_서울특별시_서초구_롯데캐슬갤럭시.pkl | 롯데캐슬갤럭시 |
| 대우아이빌 | prophet_model_서울특별시_서초구_대우아이빌.pkl | 대우아이빌 |

**주의사항**:
- 모델 파일명과 API 값이 일치해야 함
- 사용자 표시명은 UI에서만 사용

### 2. 모델 파일명 정규화

모델 파일명에서 아파트명 추출 로직:
```python
def extract_apt_name_from_model_filename(filename: str) -> str:
    """모델 파일명에서 아파트명 추출"""
    # prophet_model_서울특별시_서초구_대림서초리시온.pkl
    # -> 대림서초리시온
    if filename.startswith("prophet_model_서울특별시_서초구_"):
        apt_name = filename.replace("prophet_model_서울특별시_서초구_", "").replace(".pkl", "")
        return apt_name
    return None
```

---

## 🚀 배포 단계별 가이드

### Step 1: 코드 수정
1. `frontend/static/script.js` 수정 (UI 제한)
2. `backend/main.py` 수정 (API 제한 및 모델 매핑)

### Step 2: 배포 파일 생성
1. `Procfile` 생성
2. `runtime.txt` 생성 (선택사항)
3. `railway.json` 생성 (선택사항)

### Step 3: 로컬 테스트
1. 서버 실행: `cd backend && uvicorn main:app --host 0.0.0.0 --port 8000`
2. 브라우저에서 `http://localhost:8000` 접속
3. UI 제한 확인
4. 각 아파트 예측 테스트

### Step 4: 원격 저장소에 푸시
1. 배포 브랜치를 원격 저장소에 푸시:
   ```bash
   git checkout railway-deployment
   git push origin railway-deployment
   ```
2. GitHub에서 브랜치 확인:
   - https://github.com/jisungs/apt_astrology
   - 브랜치 목록에서 `railway-deployment` 확인

### Step 5: Railway 배포
1. Railway 계정 생성: https://railway.app
2. 새 프로젝트 생성
3. GitHub 저장소 연결:
   - 저장소: `jisungs/apt_astrology`
   - 브랜치: `railway-deployment` 선택
4. 환경 변수 설정:
   - `PUBLIC_API_KEY`: 공공데이터 포털 API 키
5. 배포 실행 (자동 또는 수동)
6. 배포 URL 확인 및 테스트

---

## ⚠️ 주의사항

### 1. 모델 파일 크기
- 모델 파일이 크므로 Git LFS 사용 고려
- 또는 Railway의 파일 시스템에 직접 업로드

### 2. 환경 변수
- `PUBLIC_API_KEY`는 Railway 대시보드에서 설정
- `.env` 파일은 Git에 커밋하지 않음

### 3. 포트 설정
- Railway는 `$PORT` 환경 변수를 자동으로 설정
- `Procfile`에서 `$PORT` 사용

### 4. 모델 파일 경로
- Railway에서 `models/` 폴더 경로 확인 필요
- 상대 경로 사용: `os.path.join(BASE_DIR, "models", ...)`

---

## 📊 예상 배포 시간

- **코드 수정**: 1-2시간
- **로컬 테스트**: 30분
- **Railway 배포**: 30분
- **총 예상 시간**: 2-3시간

---

## ✅ 완료 체크리스트

### 코드 수정
- [ ] `frontend/static/script.js` - UI 제한 구현
- [ ] `backend/main.py` - API 제한 및 모델 매핑 구현

### 배포 파일
- [ ] `Procfile` 생성
- [ ] `runtime.txt` 생성 (선택사항)
- [ ] `railway.json` 생성 (선택사항)

### 테스트
- [ ] 로컬 서버 실행 테스트
- [ ] UI 제한 확인
- [ ] 각 아파트 예측 테스트
- [ ] 모델 로드 테스트

### 원격 저장소
- [ ] 원격 저장소 연결 확인 (`git remote -v`)
- [ ] 배포 브랜치 원격 푸시 (`git push origin railway-deployment`)
- [ ] GitHub에서 브랜치 확인 (https://github.com/jisungs/apt_astrology)

### 배포
- [ ] Railway 계정 생성
- [ ] 프로젝트 생성 및 GitHub 저장소 연결 (`jisungs/apt_astrology`)
- [ ] 배포 브랜치 선택 (`railway-deployment`)
- [ ] 환경 변수 설정 (`PUBLIC_API_KEY`)
- [ ] 배포 실행
- [ ] 배포 URL 확인 및 테스트

---

## 🎯 다음 단계

1. 코드 수정 완료 후 로컬 테스트
2. 배포 브랜치를 원격 저장소에 푸시 (`git push origin railway-deployment`)
3. Railway에서 GitHub 저장소 연결 및 배포 브랜치 선택
4. Railway 배포 실행
5. 배포 후 모니터링 및 최적화

---

## 📝 Git 원격 저장소 명령어 참고

### 원격 저장소 확인
```bash
# 원격 저장소 목록 확인
git remote -v

# 출력 예시:
# origin  https://github.com/jisungs/apt_astrology.git (fetch)
# origin  https://github.com/jisungs/apt_astrology.git (push)
```

### 배포 브랜치 푸시
```bash
# 배포 브랜치로 전환
git checkout railway-deployment

# 원격 저장소에 푸시 (최초)
git push -u origin railway-deployment

# 이후 푸시
git push origin railway-deployment
```

### 원격 브랜치 확인
```bash
# 원격 브랜치 목록 확인
git branch -r

# 모든 브랜치 확인 (로컬 + 원격)
git branch -a
```

### 원격 브랜치 삭제 (필요시)
```bash
# 원격 브랜치 삭제
git push origin --delete railway-deployment
```

---

**작성자**: AI Assistant  
**최종 업데이트**: 2025년 11월 25일  
**원격 저장소**: https://github.com/jisungs/apt_astrology.git

