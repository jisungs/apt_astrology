# 🔍 Railway 배포 오류 분석 및 해결 방안

**작성일**: 2025년 11월 25일  
**에러 유형**: Python 설치 실패  
**빌드 도구**: mise

---

## 🚨 에러 메시지

```
install mise packages: python
mise python@3.11.0   install
mise ERROR failed to install core:python@3.11.0
mise ERROR no precompiled python found for core:python@3.11.0 on x86_64-unknown-linux-gnu
ERROR: failed to build: failed to solve: process "mise install" did not complete successfully: exit code: 1
```

---

## 🔍 원인 분석

### 문제 원인
1. **`runtime.txt` 파일 존재**
   - Railway가 `runtime.txt` 파일을 발견하면 `mise`를 사용하여 Python 버전을 설치하려고 시도
   - `runtime.txt`는 Heroku 스타일의 파일 형식
   - Railway는 기본적으로 Nixpacks 빌드팩을 사용하며, `runtime.txt`를 직접 지원하지 않음

2. **mise의 Python 버전 문제**
   - `mise`가 Python 3.11.0의 precompiled 버전을 찾지 못함
   - Railway의 Linux 환경(x86_64-unknown-linux-gnu)에서 해당 버전을 지원하지 않을 수 있음

3. **빌드팩 충돌**
   - Railway가 `runtime.txt`를 보고 mise를 사용하려고 하지만
   - 실제로는 Nixpacks를 사용해야 함

---

## ✅ 해결 방법

### 방법 1: runtime.txt 파일 삭제 (권장)

Railway는 `requirements.txt`를 보고 Python 버전을 자동으로 감지합니다.

**작업**:
```bash
# runtime.txt 파일 삭제
rm runtime.txt

# Git에 반영
git add runtime.txt
git commit -m "fix: Railway 배포 오류 해결 - runtime.txt 제거"
git push origin railway-deployment
```

**이유**:
- Railway는 `requirements.txt`를 분석하여 적절한 Python 버전을 자동 선택
- `runtime.txt`가 없으면 Nixpacks가 정상적으로 작동

---

### 방법 2: nixpacks.toml 파일 생성

Railway의 공식 빌드팩인 Nixpacks를 사용하여 Python 버전을 명시적으로 지정합니다.

**파일 생성**: `nixpacks.toml` (프로젝트 루트)

**내용**:
```toml
[phases.setup]
nixPkgs = ["python311"]

[phases.install]
cmds = ["pip install -r backend/requirements.txt"]

[start]
cmd = "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
```

**작업**:
```bash
# nixpacks.toml 생성
# (위 내용으로 파일 생성)

# runtime.txt 삭제
rm runtime.txt

# Git에 반영
git add nixpacks.toml
git add runtime.txt
git commit -m "fix: Railway 배포 오류 해결 - nixpacks.toml 추가, runtime.txt 제거"
git push origin railway-deployment
```

---

### 방법 3: runtime.txt 형식 변경 (비권장)

`runtime.txt`의 형식을 변경하여 Railway가 인식하지 못하도록 합니다.

**변경 전**:
```
python-3.11.0
```

**변경 후**:
```
# Railway는 이 파일을 무시하고 requirements.txt를 사용합니다
```

또는 파일명 변경:
```bash
mv runtime.txt runtime.txt.bak
```

---

## 🎯 권장 해결 방법

### Step 1: runtime.txt 삭제
```bash
cd /Users/jisungs/Documents/dev/sideprojects/apt_astrology
git rm runtime.txt
```

### Step 2: nixpacks.toml 생성 (선택사항)
Railway가 자동으로 감지하지만, 명시적으로 지정하고 싶다면:

```bash
# nixpacks.toml 파일 생성
```

### Step 3: 커밋 및 푸시
```bash
git add .
git commit -m "fix: Railway 배포 오류 해결 - runtime.txt 제거"
git push origin railway-deployment
```

---

## 📊 Railway 빌드팩 동작 방식

### Railway의 빌드팩 감지 순서
1. `nixpacks.toml` 파일 확인
2. `Procfile` 확인
3. `requirements.txt` 확인 (Python 버전 자동 감지)
4. `runtime.txt` 확인 (이 경우 mise 사용 시도 → 오류 발생)

### Python 버전 자동 감지
- Railway는 `requirements.txt`의 패키지 요구사항을 분석
- 적절한 Python 버전을 자동으로 선택
- 일반적으로 Python 3.11 이상을 사용

---

## 🔧 추가 확인 사항

### 1. requirements.txt 확인
현재 `requirements.txt`는 패키지 목록만 포함되어 있습니다.
Python 버전을 명시적으로 지정하려면:

```txt
# Python 버전 요구사항 (선택사항)
# Railway는 자동으로 적절한 버전을 선택합니다
```

### 2. Procfile 확인
현재 `Procfile`은 올바르게 설정되어 있습니다:
```
web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 3. 디렉토리 구조 확인
Railway는 프로젝트 루트에서 시작하므로:
- `backend/` 디렉토리로 이동 필요 (Procfile에 포함됨)
- `requirements.txt` 경로: `backend/requirements.txt`

---

## ⚠️ 주의사항

### 1. Python 버전 호환성
- 현재 코드는 Python 3.11 이상에서 작동해야 함
- Railway는 일반적으로 최신 Python 버전을 사용
- 특정 버전이 필요하면 `nixpacks.toml` 사용

### 2. 패키지 설치 경로
- `Procfile`에서 `cd backend` 후 실행
- `requirements.txt`는 `backend/requirements.txt`에 있음
- Railway가 자동으로 `pip install -r requirements.txt` 실행

### 3. 모델 파일 경로
- `models/` 폴더는 프로젝트 루트에 있어야 함
- Railway 배포 시 모델 파일도 함께 배포되어야 함

---

## 🚀 해결 후 재배포

### 1. 파일 수정
```bash
# runtime.txt 삭제
git rm runtime.txt

# 커밋
git commit -m "fix: Railway 배포 오류 해결 - runtime.txt 제거"
```

### 2. 푸시
```bash
git push origin railway-deployment
```

### 3. Railway 재배포
- Railway가 자동으로 재배포 시작
- 또는 Railway 대시보드에서 "Redeploy" 클릭

### 4. 배포 로그 확인
- Railway 대시보드에서 배포 로그 확인
- Python 버전이 자동으로 감지되는지 확인
- 빌드가 성공하는지 확인

---

## 📝 예상 결과

### runtime.txt 제거 후
- Railway가 `requirements.txt`를 분석
- 적절한 Python 버전 자동 선택 (보통 3.11 이상)
- Nixpacks 빌드팩 사용
- 정상적인 빌드 및 배포

### 배포 로그 예시
```
Detected Python project
Installing Python dependencies...
Successfully installed packages
Starting application...
```

---

## ✅ 체크리스트

### 해결 전
- [ ] 에러 원인 분석 완료
- [ ] 해결 방법 결정

### 해결 중
- [ ] `runtime.txt` 파일 삭제
- [ ] 변경사항 커밋
- [ ] 원격 저장소 푸시

### 해결 후
- [ ] Railway 재배포 확인
- [ ] 배포 로그 확인
- [ ] 배포 성공 확인
- [ ] 애플리케이션 동작 확인

---

**작성자**: AI Assistant  
**최종 업데이트**: 2025년 11월 25일

