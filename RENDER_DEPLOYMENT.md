# 🚀 Render 배포 가이드

W Concept 트래킹 시스템 백엔드(API + 스케줄러)를 Render에 배포하는 가이드입니다.

## 📋 목차

1. [Render 계정 설정](#1-render-계정-설정)
2. [프로젝트 배포](#2-프로젝트-배포)
3. [환경 변수 설정](#3-환경-변수-설정)
4. [배포 확인](#4-배포-확인)
5. [프론트엔드 연결](#5-프론트엔드-연결)
6. [문제 해결](#6-문제-해결)

---

## 1. Render 계정 설정

### 1.1 Render 가입
1. [Render.com](https://render.com) 접속
2. **"Get Started"** 또는 **"Sign Up"** 클릭
3. **GitHub 계정으로 로그인** 선택
4. GitHub 권한 승인

### 1.2 무료 티어 확인
- **완전 무료**: 신용카드 불필요
- **750시간/월**: 충분히 24시간 실행 가능
- **512MB RAM**: API + 스케줄러 실행에 충분
- **1GB 디스크**: 데이터베이스 저장용
- **슬립 모드**: 15분 비활성 시 슬립 (하지만 스케줄러가 매시간 실행되므로 유지됨)

---

## 2. 프로젝트 배포

### 2.1 Blueprint 방식 (추천 ⭐)

1. **Render 대시보드** 접속
2. **"New"** → **"Blueprint"** 클릭
3. **Connect Repository**: `wconcept-tracking` 선택
4. **Branch**: `genspark_ai_developer` 선택
5. **render.yaml 파일 자동 감지**
6. **"Apply"** 클릭

Render가 자동으로:
- `render.yaml` 설정 읽기
- Python 환경 설정
- 의존성 설치 (Playwright + Chromium 포함)
- 디스크 마운트 (데이터베이스 저장용)
- 서비스 시작 (API + 스케줄러)

**예상 배포 시간**: 10-15분 (Playwright 설치 포함)

### 2.2 수동 방식 (대안)

Blueprint가 작동하지 않는 경우:

1. **Render 대시보드** → **"New"** → **"Web Service"**
2. **Connect Repository**: `wconcept-tracking` 선택
3. 다음 설정 입력:

**기본 설정**:
```
Name: wconcept-tracker-backend
Region: Singapore (가장 가까운 지역)
Branch: genspark_ai_developer
Runtime: Python 3
```

**Build & Deploy**:
```
Build Command:
pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium

Start Command:
./start.sh
```

**Instance Type**:
```
Free
```

4. **Create Web Service** 클릭

---

## 3. 환경 변수 설정

### 3.1 자동 설정 (render.yaml 사용 시)

`render.yaml` 파일에 이미 환경 변수가 정의되어 있으므로 자동으로 설정됩니다.

### 3.2 수동 설정 (수동 배포 시)

Render 서비스 페이지 → **Environment** 탭:

```bash
# Python 버전
PYTHON_VERSION=3.11.6

# 데이터베이스
DATABASE_URL=sqlite:///./wconcept_tracking.db

# API 설정
API_HOST=0.0.0.0
PORT=10000

# Playwright 설정
PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/.playwright

# 크롤링 설정
SCRAPE_PRODUCT_LIMIT=200
CHROME_HEADLESS=true

# 로깅
LOG_LEVEL=INFO
```

**"Save Changes"** 클릭 → 자동 재배포

---

## 4. 배포 확인

### 4.1 배포 로그 확인

1. Render 서비스 페이지 → **Logs** 탭
2. 다음 메시지 확인:

```
==> Installing dependencies from requirements.txt
==> Installing Playwright...
==> Building...
==> Starting service with './start.sh'

🚀 Starting W Concept Tracker Backend...
📊 Initializing database...
⏰ Starting scheduler...
🌐 Starting API server...
✅ Backend services started:
   - API Server (PID: XXXX)
   - Scheduler (PID: XXXX)
⏰ 다음 실행 예정: 2025-10-23 17:16:00 (약 XX분 후)

==> Your service is live 🎉
```

### 4.2 서비스 URL 확인

1. Render 서비스 페이지 상단에 **URL 표시**
   - 예: `https://wconcept-tracker-backend.onrender.com`
2. 이 URL이 **API 서버 주소**입니다

### 4.3 API 테스트

```bash
# Health check
curl https://wconcept-tracker-backend.onrender.com/api/health

# 예상 응답:
{
  "status": "healthy",
  "timestamp": "2025-10-23T16:45:00Z",
  "database": "connected",
  "scheduler": "running"
}

# 카테고리별 최신 업데이트 시간
curl https://wconcept-tracker-backend.onrender.com/api/categories/update-times

# 특정 카테고리 제품 조회
curl https://wconcept-tracker-backend.onrender.com/api/products/outer?limit=10
```

---

## 5. 프론트엔드 연결

### 5.1 Cloudflare Pages 환경 변수 업데이트

1. **Cloudflare Pages 대시보드** 접속
2. **wconcept-tracking-dashboard** 프로젝트 선택
3. **Settings** → **Environment Variables**
4. 다음 변수 추가/수정:

```bash
VITE_API_URL=https://wconcept-tracker-backend.onrender.com
```

5. **Save** 클릭
6. **Deployments** 탭 → **Retry deployment** 또는 새로 커밋하여 재배포

### 5.2 로컬 개발 환경 설정

`dashboard/.env` 파일 생성:

```bash
VITE_API_URL=https://wconcept-tracker-backend.onrender.com
```

로컬에서 테스트:
```bash
cd dashboard
npm run dev
```

---

## 6. 문제 해결

### 6.1 Playwright 설치 실패

**증상**: "chromium executable not found" 오류

**해결**:
1. **빌드 명령어 확인**:
   ```bash
   pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium
   ```
2. **환경 변수 확인**: `PLAYWRIGHT_BROWSERS_PATH` 설정 확인
3. **재배포**: Render 서비스 → **Manual Deploy** → **Deploy latest commit**

### 6.2 서비스가 슬립 모드로 진입

**증상**: 첫 요청이 느리거나 타임아웃

**원인**: Render 무료 티어는 15분 비활성 시 슬립

**해결** (스케줄러가 이미 해결함):
- 스케줄러가 매시간 실행되므로 서비스가 슬립 모드로 들어가지 않음
- 만약 슬립된다면: 첫 요청 시 30초 정도 대기 (웜업 시간)

### 6.3 스케줄러가 실행되지 않음

**증상**: 매시간 :16분에 크롤링이 안 됨

**해결**:
1. **로그 확인**: `⏰ Starting scheduler...` 메시지 확인
2. **start.sh 권한 확인**: 이미 실행 권한 부여됨 (`chmod +x start.sh`)
3. **프로세스 확인**: 로그에서 두 PID (API + Scheduler) 확인
4. **재배포**: Manual Deploy

### 6.4 CORS 오류

**증상**: 프론트엔드에서 API 호출 시 CORS 오류

**해결**:
- `api.py`의 CORS 설정이 모든 origin 허용 (`allow_origins=["*"]`)
- 여전히 오류 발생 시:
  1. Render 서비스 → Environment → `CORS_ORIGINS` 추가
  2. 값: `https://your-frontend.pages.dev,http://localhost:5173`

### 6.5 데이터베이스 파일 손실

**증상**: 재배포 후 데이터가 사라짐

**원인**: Render 무료 티어는 기본적으로 휘발성 파일 시스템

**해결** (render.yaml에 이미 설정됨):
```yaml
disk:
  name: wconcept-data
  mountPath: /opt/render/project/src
  sizeGB: 1
```

이 설정으로 데이터베이스가 디스크에 영구 저장됩니다.

### 6.6 빌드 타임아웃

**증상**: 빌드 중 15분 타임아웃 오류

**원인**: Playwright + Chromium 설치 시간이 오래 걸림

**해결**:
- Render는 무료 티어에서 빌드 타임아웃이 없음 (충분한 시간 제공)
- 네트워크 문제일 수 있으니 재시도: **Manual Deploy** 클릭

### 6.7 메모리 부족

**증상**: "Out of memory" 또는 "Killed" 오류

**원인**: 무료 티어는 512MB RAM 제한

**해결**:
1. **크롤링 제한 줄이기**:
   - Environment → `SCRAPE_PRODUCT_LIMIT=100` (200 → 100)
2. **로깅 줄이기**:
   - Environment → `LOG_LEVEL=WARNING`
3. **유료 플랜**: 더 많은 메모리 필요 시 Starter 플랜 ($7/월, 1GB RAM)

---

## 📊 배포 후 확인 사항

### ✅ 체크리스트

- [ ] Render 배포 성공 (Live 상태, 초록불)
- [ ] 서비스 URL 접근 가능
- [ ] API Health Check 응답 정상
- [ ] 로그에서 스케줄러 시작 메시지 확인
- [ ] 프론트엔드에서 데이터 로드 정상
- [ ] 매시간 :16분에 자동 크롤링 실행 확인
- [ ] 카테고리별 데이터 수집 정상 (8개 카테고리)

---

## 🔧 유용한 Render 기능

### 로그 스트리밍
```bash
# 실시간 로그 확인 (Render 대시보드)
Logs 탭 → "Follow logs" 체크
```

### 수동 재배포
```bash
# Render 대시보드
Manual Deploy → Deploy latest commit
```

### Shell 접속
```bash
# Render 대시보드
Shell 탭 → 터미널 접속 가능
```

### 메트릭 모니터링
```bash
# Render 대시보드
Metrics 탭 → CPU, 메모리, 네트워크 모니터링
```

---

## 🎯 스케줄러 작동 방식

### 실행 주기
- **매시간 16분**: 00:16, 01:16, 02:16, 03:16, ...
- **8개 카테고리 순차 크롤링**:
  1. 아우터 (200개)
  2. 원피스 (200개)
  3. 블라우스 (200개)
  4. 셔츠 (200개)
  5. 티셔츠 (200개)
  6. 니트 (200개)
  7. 스커트 (200개)
  8. 언더웨어 (200개)

### 예상 실행 시간
- **크롤링 시간**: 약 5-10분 (8개 카테고리 × 200개)
- **총 제품 수**: 1,600개/시간

### 로그 확인
```bash
# 스케줄러 시작
⏰ Starting scheduler...
⏰ 다음 실행 예정: 2025-10-23 17:16:00 (약 45분 후)

# 크롤링 시작
🔍 Starting scheduled crawl...
📊 크롤링 시작: outer (아우터)
✅ outer: 200개 제품 수집 완료

# 크롤링 완료
✅ 전체 크롤링 완료: 8개 카테고리, 1600개 제품
```

---

## 🆚 Render vs Railway 비교

| 항목 | Render (무료) | Railway (유료) |
|------|---------------|----------------|
| **가격** | 완전 무료 | $5/월부터 |
| **RAM** | 512MB | 512MB+ |
| **디스크** | 1GB 영구 저장 | 1GB+ |
| **슬립** | 15분 후 (스케줄러가 방지) | 없음 |
| **빌드 시간** | 제한 없음 | 제한 없음 |
| **GitHub 연동** | ✅ | ✅ |
| **추천** | ✅ 무료로 충분 | 유료 플랜 필요 시 |

---

## 🚀 다음 단계

1. ✅ Render 계정 생성
2. ✅ Blueprint로 배포 (render.yaml 자동 적용)
3. ✅ 배포 로그에서 성공 확인
4. ✅ API URL 복사
5. ✅ Cloudflare Pages에 API URL 설정
6. ⏰ 첫 자동 크롤링 대기 (다음 :16분)
7. 📊 데이터 수집 확인
8. 🎉 완료!

---

## 💡 팁

### 무료 티어 최적화
- 로그 레벨을 WARNING으로 설정하여 로그 줄이기
- 불필요한 파일 정리하여 디스크 공간 절약

### 슬립 모드 방지
- 스케줄러가 매시간 실행되므로 자동으로 방지됨
- 추가로 외부 Uptime 모니터 사용 가능 (UptimeRobot 등)

### 디스크 영구 저장
- `render.yaml`의 `disk` 설정으로 데이터베이스 영구 저장
- 재배포 시에도 데이터 유지

### GitHub 자동 배포
- `genspark_ai_developer` 브랜치에 push 시 자동 재배포
- 설정 변경 시 자동 반영

---

## 📞 지원

- **Render 문서**: https://render.com/docs
- **Render Community**: https://community.render.com
- **GitHub Issues**: 프로젝트 저장소에서 이슈 생성

---

## 🎉 완료!

Render 배포 설정이 완료되었습니다. 이제 Render 대시보드에서 Blueprint를 생성하고 배포를 시작하세요!

**배포 완료 후 Render URL을 Cloudflare Pages에 연결하는 것을 잊지 마세요!** 🎯
