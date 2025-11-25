# 🌿 Git 브랜치 전략

**작성일**: 2025년 11월 25일  
**목적**: 개발 버전과 배포 버전 분리 관리

---

## 📋 브랜치 구조

### 주요 브랜치
- **master**: 개발 버전 (전체 기능 포함, 모든 지역/아파트 지원)
- **railway-deployment**: 배포 버전 (서초구 제한 버전, Railway 배포용)

---

## 🔄 브랜치 전략

### 개발 워크플로우

#### 1. 개발 작업 (master 브랜치)
```bash
# master 브랜치에서 개발
git checkout master

# 기능 개발 및 커밋
git add .
git commit -m "feat: 새로운 기능 추가"

# 원격 저장소에 푸시
git push origin master
```

#### 2. 배포 작업 (railway-deployment 브랜치)
```bash
# 배포 브랜치로 전환
git checkout railway-deployment

# master 브랜치의 최신 변경사항 병합 (필요시)
git merge master

# 배포 관련 변경사항 커밋
git add .
git commit -m "feat: Railway 배포용 서초구 제한 버전 구현"

# 원격 저장소에 푸시
git push origin railway-deployment
```

#### 3. 배포 후 업데이트
```bash
# 배포 후 master 브랜치로 변경사항 병합 (선택사항)
git checkout master
git merge railway-deployment

# 또는 배포 브랜치의 특정 변경사항만 cherry-pick
git cherry-pick <commit-hash>
```

---

## 🎯 브랜치별 차이점

### master 브랜치
- **목적**: 개발 및 테스트
- **기능**: 전체 지역 및 아파트 지원
- **모델**: 동적 학습 (필요시 새 모델 생성)
- **UI**: 모든 시/도, 구/군 선택 가능
- **API**: 전체 데이터 수집 및 예측

### railway-deployment 브랜치
- **목적**: Railway 프로덕션 배포
- **기능**: 서초구 및 지정된 5개 아파트만 지원
- **모델**: 기존 학습된 모델만 사용 (5개)
- **UI**: 서울특별시 서초구만 선택 가능
- **API**: 제한된 데이터만 반환

---

## 📝 배포 브랜치 전용 변경사항

### 1. UI 제한 (`frontend/static/script.js`)
- 시/도 드롭다운: 서울특별시만 표시
- 구/군 드롭다운: 서초구만 표시
- 아파트 드롭다운: 지정된 5개만 표시

### 2. API 제한 (`backend/main.py`)
- `/api/cities`: 서울특별시만 반환
- `/api/districts`: 서초구만 반환
- `/api/apartments`: 지정된 5개 아파트만 반환
- `/predict`: 주소 및 아파트명 검증

### 3. 모델 매핑 (`backend/main.py`)
- `MODEL_FILE_MAPPING`: 5개 아파트만 매핑
- 기존 모델 파일만 사용 (학습 없음)

---

## 🚀 Railway 배포 설정

### 브랜치 연결
Railway에서 배포 브랜치를 지정:
1. Railway 프로젝트 설정
2. Source → Branch 선택
3. `railway-deployment` 브랜치 선택

### 자동 배포
- `railway-deployment` 브랜치에 푸시하면 자동 배포
- master 브랜치는 개발용으로 유지

---

## 📊 브랜치 관리 체크리스트

### 배포 전
- [ ] `railway-deployment` 브랜치 생성 확인
- [ ] master 브랜치의 최신 변경사항 병합 (필요시)
- [ ] 배포 관련 변경사항 커밋
- [ ] 로컬 테스트 완료

### 배포 후
- [ ] Railway 배포 성공 확인
- [ ] 배포 환경 테스트 완료
- [ ] master 브랜치에 변경사항 병합 (선택사항)

---

## ⚠️ 주의사항

### 1. 브랜치 분리
- master와 railway-deployment는 독립적으로 관리
- 배포 브랜치의 변경사항은 master에 자동 병합되지 않음

### 2. 충돌 해결
- 병합 시 충돌 발생 가능
- 배포 브랜치의 제한 로직이 master의 전체 기능과 충돌할 수 있음
- 충돌 시 수동으로 해결 필요

### 3. 모델 파일
- 두 브랜치 모두 `models/` 폴더의 모델 파일 사용
- 배포 브랜치는 5개 모델만 필요
- master 브랜치는 모든 모델 사용 가능

---

## 🔧 유용한 Git 명령어

### 브랜치 확인
```bash
# 현재 브랜치 확인
git branch

# 모든 브랜치 확인
git branch -a

# 브랜치 간 차이 확인
git diff master..railway-deployment
```

### 브랜치 전환
```bash
# master 브랜치로 전환
git checkout master

# 배포 브랜치로 전환
git checkout railway-deployment
```

### 병합
```bash
# master의 변경사항을 배포 브랜치에 병합
git checkout railway-deployment
git merge master

# 배포 브랜치의 변경사항을 master에 병합 (선택사항)
git checkout master
git merge railway-deployment
```

### 원격 저장소
```bash
# 원격 브랜치 확인
git branch -r

# 원격 브랜치로 푸시
git push origin railway-deployment

# 원격 브랜치 삭제
git push origin --delete railway-deployment
```

---

## 📈 브랜치 전략 다이어그램

```
master (개발)
  │
  ├─── 기능 개발
  ├─── 버그 수정
  └─── 전체 기능 테스트
       │
       │ (병합)
       ↓
railway-deployment (배포)
  │
  ├─── UI 제한
  ├─── API 제한
  ├─── 모델 매핑
  └─── Railway 배포
```

---

**작성자**: AI Assistant  
**최종 업데이트**: 2025년 11월 25일

