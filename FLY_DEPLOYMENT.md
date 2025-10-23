# ✈️ Fly.io 배포 가이드

W Concept 트래킹 시스템 백엔드(API + 스케줄러)를 Fly.io에 배포하는 가이드입니다.

## 📋 목차

1. [Fly.io 소개](#1-flyio-소개)
2. [Fly CLI 설치](#2-fly-cli-설치)
3. [프로젝트 배포](#3-프로젝트-배포)
4. [배포 확인](#4-배포-확인)
5. [프론트엔드 연결](#5-프론트엔드-연결)
6. [문제 해결](#6-문제-해결)

---

## 1. Fly.io 소개

### 🎯 Fly.io를 선택한 이유

| 항목 | Fly.io (무료) | Render (무료) |
|------|---------------|---------------|
| **Playwright 지원** | ✅ 우수 | ⚠️ 제한적 |
| **메모리** | 256MB (무료) | 512MB |
| **슬립 모드** | 설정 가능 (방지 가능) | 15분 후 |
| **Docker 지원** | ✅ 네이티브 | ❌ 제한적 |
| **빌드 안정성** | ✅ 높음 | ⚠️ 중간 |
| **무료 티어** | ✅ 영구 무료 | ✅ 영구 무료 |

**Fly.io 장점**:
- Docker 기반으로 Playwright 설치 안정적
- 리소스 제약이 덜함
- 한국과 가까운 Singapore 리전 제공
- 슬립 모드 제어 가능

---

## 2. Fly CLI 설치

### 2.1 macOS/Linux
```bash
curl -L https://fly.io/install.sh | sh
```

### 2.2 Windows (PowerShell)
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

### 2.3 설치 확인
```bash
fly version
```

---

## 3. 프로젝트 배포

### 3.1 Fly.io 로그인

```bash
fly auth login
```

브라우저가 열리면 GitHub 계정으로 로그인하세요.

### 3.2 프로젝트 디렉토리로 이동

```bash
cd /path/to/wconcept-tracking
git checkout genspark_ai_developer
```

### 3.3 Fly.io 앱 생성

```bash
fly apps create wconcept-tracker-backend --org personal
```

**또는** 자동 이름 생성:
```bash
fly apps create --org personal
```

### 3.4 배포 시작

```bash
fly deploy
```

이 명령어가 자동으로:
- ✅ Dockerfile을 사용하여 Docker 이미지 빌드
- ✅ Playwright + Chromium 설치
- ✅ 이미지를 Fly.io 레지스트리에 푸시
- ✅ 앱 배포 및 시작

**예상 배포 시간**: 5-10분

### 3.5 배포 로그 확인

```bash
fly logs
```

다음 메시지를 확인하세요:
```
🚀 Starting W Concept Tracker Backend...
📊 Initializing database...
⏰ Starting scheduler...
🌐 Starting API server...
✅ Backend services started
```

---

## 4. 배포 확인

### 4.1 앱 상태 확인

```bash
fly status
```

출력 예시:
```
App
  Name     = wconcept-tracker-backend
  Owner    = personal
  Hostname = wconcept-tracker-backend.fly.dev
  Platform = nomad
  Status   = running
```

### 4.2 앱 URL 확인

```bash
fly info
```

**URL**: `https://wconcept-tracker-backend.fly.dev`

### 4.3 API 테스트

```bash
# Health check
curl https://wconcept-tracker-backend.fly.dev/api/health

# 예상 응답:
{
  "status": "healthy",
  "timestamp": "2025-10-24T02:30:00Z",
  "database": "connected",
  "scheduler": "running"
}

# 카테고리별 업데이트 시간
curl https://wconcept-tracker-backend.fly.dev/api/categories/update-times

# 제품 조회
curl https://wconcept-tracker-backend.fly.dev/api/products/outer?limit=10
```

### 4.4 실시간 로그 모니터링

```bash
fly logs --tail
```

---

## 5. 프론트엔드 연결

### 5.1 Cloudflare Pages 환경 변수 업데이트

1. **Cloudflare Pages 대시보드** 접속
2. **wconcept-tracking-dashboard** 프로젝트 선택
3. **Settings** → **Environment Variables**
4. 다음 변수 추가/수정:

```bash
VITE_API_URL=https://wconcept-tracker-backend.fly.dev
```

5. **Save** → **Redeploy**

### 5.2 로컬 개발 환경 설정

`dashboard/.env` 파일 생성:

```bash
VITE_API_URL=https://wconcept-tracker-backend.fly.dev
```

---

## 6. 문제 해결

### 6.1 배포 실패

**증상**: `fly deploy` 실패

**해결**:
```bash
# 로그 확인
fly logs

# 특정 에러에 따라 대응:
# - 메모리 부족: fly.toml에서 memory를 512mb로 증가
# - Dockerfile 오류: Dockerfile 문법 확인
```

### 6.2 Playwright 설치 실패

**증상**: "chromium executable not found"

**해결**:
Dockerfile에 이미 모든 시스템 의존성이 포함되어 있습니다. 재배포 시도:
```bash
fly deploy --force
```

### 6.3 앱이 시작되지 않음

**증상**: `fly status` 결과 "stopped" 또는 "crashed"

**해결**:
```bash
# 로그 확인
fly logs

# 스케일 조정
fly scale count 1

# 재시작
fly apps restart wconcept-tracker-backend
```

### 6.4 Health Check 실패

**증상**: 앱이 재시작을 반복

**해결**:
1. Health check 엔드포인트 확인:
   ```bash
   curl https://wconcept-tracker-backend.fly.dev/api/health
   ```
2. `api.py`에 `/api/health` 엔드포인트가 있는지 확인
3. 필요시 `fly.toml`의 health check 경로 수정

### 6.5 메모리 부족

**증상**: "Out of memory" 또는 "Killed"

**해결**:

**방법 1: 메모리 증가** (무료 티어 제한 내)
```bash
fly scale memory 512
```

**방법 2: 크롤링 제한 줄이기**
`fly.toml`에서:
```toml
[env]
  SCRAPE_PRODUCT_LIMIT = "100"  # 200 → 100
```

재배포:
```bash
fly deploy
```

### 6.6 슬립 모드

**증상**: 앱이 비활성 시 슬립 모드로 진입

**현재 설정**:
`fly.toml`에 이미 슬립 방지 설정이 되어 있습니다:
```toml
auto_stop_machines = false
min_machines_running = 1
```

스케줄러가 매시간 실행되므로 추가 조치 불필요.

### 6.7 데이터베이스 영구 저장

**증상**: 재배포 시 데이터가 사라짐

**해결**: Fly.io Volume 사용

```bash
# Volume 생성 (1GB)
fly volumes create wconcept_data --size 1 --region sin

# fly.toml에 추가:
[[mounts]]
  source = "wconcept_data"
  destination = "/app/data"

# DATABASE_URL 수정:
[env]
  DATABASE_URL = "sqlite:////app/data/wconcept_tracking.db"

# 재배포
fly deploy
```

---

## 🔧 유용한 Fly.io 명령어

### 앱 관리
```bash
# 앱 목록
fly apps list

# 앱 정보
fly info

# 앱 상태
fly status

# 앱 재시작
fly apps restart wconcept-tracker-backend
```

### 로그
```bash
# 최근 로그
fly logs

# 실시간 로그
fly logs --tail

# 특정 인스턴스 로그
fly logs --instance <instance-id>
```

### 스케일링
```bash
# 메모리 조정
fly scale memory 512

# 인스턴스 수 조정
fly scale count 1

# 현재 스케일 확인
fly scale show
```

### SSH 접속
```bash
# 컨테이너에 SSH 접속
fly ssh console

# 명령어 실행
fly ssh console -C "ls -la /app"
```

### 환경 변수
```bash
# 환경 변수 설정
fly secrets set DATABASE_URL="sqlite:///./wconcept_tracking.db"

# 환경 변수 목록
fly secrets list

# 환경 변수 삭제
fly secrets unset KEY_NAME
```

---

## 🎯 스케줄러 작동 확인

### 로그에서 스케줄러 확인
```bash
fly logs --tail
```

**예상 로그**:
```
⏰ 다음 실행 예정: 2025-10-24 03:16:00 (약 45분 후)
🔍 Starting scheduled crawl...
📊 크롤링 시작: outer (아우터)
✅ outer: 200개 제품 수집 완료
...
✅ 전체 크롤링 완료: 8개 카테고리, 1600개 제품
```

---

## 📊 배포 후 체크리스트

### ✅ 필수 확인 사항

- [ ] `fly deploy` 성공
- [ ] `fly status` 결과 "running"
- [ ] `fly info`에서 URL 확인
- [ ] Health check API 응답 정상
- [ ] 스케줄러 로그 확인 ("⏰ 다음 실행 예정")
- [ ] Cloudflare Pages에 API URL 연결
- [ ] 프론트엔드에서 데이터 로드 정상
- [ ] 매시간 :16분에 크롤링 실행 확인

---

## 🆚 플랫폼 비교

| 항목 | Fly.io | Render | Railway |
|------|--------|--------|---------|
| **가격** | 무료 (제한적) | 무료 | 유료 ($5/월~) |
| **Playwright** | ✅ 우수 | ⚠️ 제한적 | ✅ 우수 |
| **메모리** | 256-512MB | 512MB | 512MB+ |
| **배포 방식** | Docker | Native | Native |
| **안정성** | ✅ 높음 | ⚠️ 중간 | ✅ 높음 |
| **추천** | ✅ 추천 | 대안 | 유료 시 |

---

## 🚀 다음 단계

1. ✅ Fly CLI 설치
2. ✅ `fly auth login`
3. ✅ `fly deploy`
4. ✅ API URL 확인
5. ✅ Cloudflare Pages 연결
6. ⏰ 스케줄러 작동 확인
7. 🎉 완료!

---

## 💡 팁

### 무료 티어 최적화
- 메모리: 256MB로 시작, 필요 시 512MB로 증가
- 크롤링 제한: 200개 → 100개로 줄이기
- 로그 레벨: WARNING으로 설정

### 자동 배포
GitHub Actions를 사용하여 push 시 자동 배포 가능

### 모니터링
- `fly logs --tail`로 실시간 모니터링
- `fly status`로 주기적 상태 확인

---

## 📞 지원

- **Fly.io 문서**: https://fly.io/docs
- **Fly.io 커뮤니티**: https://community.fly.io
- **GitHub Issues**: 프로젝트 저장소에서 이슈 생성

---

**배포 성공을 기원합니다!** ✈️🎉
