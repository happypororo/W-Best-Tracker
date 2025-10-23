# 🚂 Railway 배포 가이드

W Concept 트래킹 시스템 백엔드(API + 스케줄러)를 Railway에 배포하는 가이드입니다.

## 📋 목차

1. [Railway 계정 설정](#1-railway-계정-설정)
2. [프로젝트 배포](#2-프로젝트-배포)
3. [환경 변수 설정](#3-환경-변수-설정)
4. [배포 확인](#4-배포-확인)
5. [프론트엔드 연결](#5-프론트엔드-연결)
6. [문제 해결](#6-문제-해결)

---

## 1. Railway 계정 설정

### 1.1 Railway 가입
1. [Railway.app](https://railway.app) 접속
2. "Start a New Project" 또는 "Login with GitHub" 클릭
3. GitHub 계정으로 로그인

### 1.2 무료 티어 확인
- **무료 크레딧**: $5/월
- **충분한 리소스**: API + 스케줄러 실행 가능
- **자동 슬립 없음**: 24시간 실행 유지

---

## 2. 프로젝트 배포

### 2.1 New Project 생성
1. Railway 대시보드에서 **"New Project"** 클릭
2. **"Deploy from GitHub repo"** 선택
3. **"wconcept-tracking"** 저장소 선택
4. **Branch**: `genspark_ai_developer` 선택 (또는 `main`)

### 2.2 자동 배포 시작
Railway가 자동으로:
- 저장소 클론
- `requirements.txt`에서 의존성 설치
- `Procfile`에 따라 서비스 시작
- Playwright 및 Chromium 설치

**예상 배포 시간**: 5-10분

---

## 3. 환경 변수 설정

Railway 프로젝트 설정에서 환경 변수를 추가합니다.

### 3.1 필수 환경 변수

Railway 대시보드 → **Variables** 탭에서 추가:

```bash
# 데이터베이스 (Railway가 SQLite 파일 유지)
DATABASE_URL=sqlite:///./wconcept_tracking.db

# API 설정
API_HOST=0.0.0.0
PORT=8000

# Playwright 설정 (Railway 환경)
PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/.playwright
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# 크롤링 설정
SCRAPE_PRODUCT_LIMIT=200
CHROME_HEADLESS=true
```

### 3.2 선택적 환경 변수

```bash
# 로깅
LOG_LEVEL=INFO

# 크롤링 간격
SCRAPE_INTERVAL_HOURS=1
```

---

## 4. 배포 확인

### 4.1 배포 로그 확인
1. Railway 프로젝트 → **Deployments** 탭
2. 최신 배포 클릭
3. 로그에서 다음 메시지 확인:

```
🚀 Starting W Concept Tracker Backend...
📊 Initializing database...
⏰ Starting scheduler...
🌐 Starting API server...
✅ Backend services started:
   - API Server (PID: XXXX)
   - Scheduler (PID: XXXX)
⏰ 다음 실행 예정: YYYY-MM-DD HH:16:00
```

### 4.2 서비스 URL 확인
1. Railway 프로젝트 → **Settings** 탭
2. **Domains** 섹션에서 자동 생성된 URL 확인
   - 예: `https://your-project.up.railway.app`
3. 이 URL이 **API 서버 주소**입니다

### 4.3 API 테스트
```bash
# Health check
curl https://your-project.up.railway.app/api/health

# 카테고리별 최신 업데이트 시간
curl https://your-project.up.railway.app/api/categories/update-times

# 특정 카테고리 제품 조회
curl https://your-project.up.railway.app/api/products/outer?limit=10
```

---

## 5. 프론트엔드 연결

### 5.1 Cloudflare Pages 환경 변수 업데이트

Cloudflare Pages 대시보드에서:

1. **wconcept-tracking-dashboard** 프로젝트 선택
2. **Settings** → **Environment Variables**
3. 다음 변수 추가/수정:

```bash
VITE_API_URL=https://your-project.up.railway.app
```

4. **Save** 후 **Redeploy** 실행

### 5.2 로컬 개발 환경 설정

`dashboard/.env` 파일 생성:

```bash
VITE_API_URL=https://your-project.up.railway.app
```

---

## 6. 문제 해결

### 6.1 Playwright 설치 실패

**증상**: "Executable doesn't exist" 오류

**해결**:
- `nixpacks.toml` 파일 확인
- 환경 변수에 `PLAYWRIGHT_BROWSERS_PATH` 설정 확인

### 6.2 스케줄러가 실행되지 않음

**증상**: 자동 크롤링이 작동하지 않음

**해결**:
1. Railway 로그 확인: `⏰ Starting scheduler...` 메시지 확인
2. `start.sh`가 실행 권한을 가지는지 확인 (이미 설정됨)
3. 재배포: **Deployments** → **Redeploy**

### 6.3 CORS 오류

**증상**: 프론트엔드에서 API 호출 실패

**해결**:
- `api.py`의 CORS 설정 확인
- 현재 모든 origin 허용 (`allow_origins=["*"]`)
- 필요시 특정 도메인만 허용하도록 수정

### 6.4 데이터베이스 파일 손실

**증상**: 재배포 후 데이터가 사라짐

**해결**:
- Railway는 기본적으로 파일을 유지하지만, 볼륨 마운트 권장
- **Settings** → **Volumes** → **Add Volume**
- Path: `/app` (프로젝트 루트)

### 6.5 메모리 부족

**증상**: "Out of memory" 오류

**해결**:
- 무료 티어는 512MB RAM 제공
- `SCRAPE_PRODUCT_LIMIT` 줄이기 (예: 200 → 100)
- 유료 플랜으로 업그레이드

---

## 📊 배포 후 확인 사항

### ✅ 체크리스트

- [ ] Railway 배포 성공 (초록색 체크마크)
- [ ] API Health Check 응답 정상
- [ ] 스케줄러 로그 확인 ("⏰ 다음 실행 예정" 메시지)
- [ ] 프론트엔드에서 데이터 로드 정상
- [ ] 매시간 :16분에 자동 크롤링 실행 확인
- [ ] 카테고리별 데이터 수집 정상

---

## 🔧 유용한 Railway 명령어

### CLI 설치 (선택적)
```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인
railway login

# 프로젝트 연결
railway link

# 로그 실시간 확인
railway logs

# 환경 변수 설정
railway variables set KEY=VALUE
```

---

## 📈 모니터링

### Railway 대시보드에서 모니터링 가능:
- **Metrics**: CPU, 메모리, 네트워크 사용량
- **Logs**: 실시간 로그 스트리밍
- **Deployments**: 배포 히스토리 및 상태

### 권장 모니터링 포인트:
1. **매시간 :16분**: 스케줄러 실행 로그 확인
2. **메모리 사용량**: 512MB 한도 모니터링
3. **API 응답 시간**: 느려지면 최적화 필요

---

## 🚀 다음 단계

1. ✅ Railway 배포 완료
2. ✅ 프론트엔드 API URL 업데이트
3. ⏰ 첫 자동 크롤링 대기 (다음 :16분)
4. 📊 데이터 수집 확인
5. 🎉 완료!

---

## 💡 팁

- **무료 티어 최적화**: 불필요한 로그 줄이기
- **배포 자동화**: GitHub push 시 자동 재배포
- **볼륨 사용**: 데이터 지속성 보장
- **환경 변수**: 민감한 정보는 Railway Variables 사용

---

## 📞 지원

- **Railway 문서**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **GitHub Issues**: 프로젝트 저장소에서 이슈 생성

---

**배포 완료 후 Railway URL을 프론트엔드에 연결하는 것을 잊지 마세요!** 🎯
