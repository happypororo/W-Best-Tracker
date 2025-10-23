# 🚀 빠른 배포 가이드

## ✅ 완료된 작업

### 1. 데이터 수집 ✅
- **총 1,676개 제품** 수집 완료
- **398개 브랜드** 등록
- **8개 카테고리** 전체 크롤링
  - 아우터 (200개)
  - 원피스 (200개)
  - 블라우스 (200개)
  - 셔츠 (200개)
  - 티셔츠 (200개)
  - 니트 (200개)
  - 스커트 (200개)
  - 언더웨어 (200개)

### 2. GitHub 푸시 ✅
- 저장소: https://github.com/happypororo/W-Best-Tracker
- 브랜치: `genspark_ai_developer`
- Pull Request: https://github.com/happypororo/W-Best-Tracker/pull/1

---

## 🎯 지금 바로 배포하기

### 1단계: GitHub PR 머지 (30초)

1. PR 링크 접속: https://github.com/happypororo/W-Best-Tracker/pull/1
2. `Merge pull request` 버튼 클릭
3. `Confirm merge` 클릭

### 2단계: Cloudflare Pages 배포 (5분)

#### A. Cloudflare 계정 만들기
1. https://dash.cloudflare.com/ 접속
2. 계정 생성 (무료)

#### B. Pages 프로젝트 생성
1. 좌측 메뉴 `Workers & Pages` 클릭
2. `Create application` 버튼
3. `Pages` 탭 → `Connect to Git`

#### C. GitHub 연결
1. GitHub 계정 연결 승인
2. `W-Best-Tracker` 저장소 선택
3. `Begin setup` 클릭

#### D. 빌드 설정
```
Project name: wconcept-dashboard
Production branch: main
Framework preset: Vite
Build command: cd dashboard && npm install && npm run build
Build output directory: dashboard/dist
Root directory: (비워두기)
```

#### E. 환경 변수 설정
**중요!** 아래 환경 변수를 추가하세요:
```
Variable name: VITE_API_BASE_URL
Value: https://8000-is73bj77dclhgdm3vfpjp-2e77fc33.sandbox.novita.ai
```

⚠️ **주의**: 이 URL은 임시 샌드박스 URL입니다. 
다음 단계에서 영구 API 서버를 배포하고 이 값을 업데이트해야 합니다!

#### F. 배포 시작
1. `Save and Deploy` 클릭
2. 빌드 완료 대기 (2-3분)
3. 배포 완료! 🎉

**배포된 URL**: `https://wconcept-dashboard.pages.dev`
(Cloudflare가 자동으로 제공)

---

### 3단계: API 서버 배포 (10분)

#### 옵션 1: Render.com (추천 - 가장 쉬움) ⭐

1. **Render.com 가입**
   - https://render.com 접속
   - GitHub로 로그인

2. **New Web Service 생성**
   - Dashboard → `New +` → `Web Service`
   - GitHub 저장소 `W-Best-Tracker` 선택

3. **설정**
   ```
   Name: wconcept-api
   Branch: main
   Root Directory: (비워두기)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn api:app --host 0.0.0.0 --port $PORT
   ```

4. **환경 변수** (선택사항)
   ```
   PYTHON_VERSION: 3.12
   ```

5. **Create Web Service** 클릭
   - 빌드 시작 (5-7분)
   - URL 확인: `https://wconcept-api.onrender.com`

6. **Cloudflare 환경 변수 업데이트**
   - Cloudflare Pages → Settings → Environment variables
   - `VITE_API_BASE_URL` 값을 Render URL로 변경
   ```
   https://wconcept-api.onrender.com
   ```
   - `Retry deployment` 클릭하여 재배포

#### 옵션 2: Railway.app (빠름)

1. https://railway.app 접속
2. `Deploy from GitHub repo` 선택
3. `W-Best-Tracker` 저장소 선택
4. `Deploy Now` 클릭
5. Settings → Generate Domain → URL 복사
6. Cloudflare 환경 변수 업데이트

#### 옵션 3: Fly.io (고성능)

```bash
# 로컬에서 실행 (또는 샌드박스에서)
curl -L https://fly.io/install.sh | sh
flyctl auth login
cd /home/user/webapp
flyctl launch --name wconcept-api
flyctl deploy
```

---

## ✅ 배포 확인

### 프론트엔드 확인
1. Cloudflare Pages URL 접속
2. 대시보드가 로드되는지 확인
3. F12 → Console에서 에러 확인

### API 연결 확인
1. 브라우저 F12 → Network 탭
2. API 요청 확인 (`/api/products/current` 등)
3. 데이터가 정상적으로 표시되는지 확인

### 모든 기능 테스트
- ✅ TOP 10 제품 표시
- ✅ 카테고리 필터 (아우터, 원피스 등)
- ✅ 브랜드 통계 차트
- ✅ 브랜드 필터링
- ✅ 순위 동향 차트

---

## 🔄 자동 업데이트 설정

### GitHub Actions로 자동 크롤링 (선택사항)

`.github/workflows/scrape.yml` 파일을 추가하면 매일 자동으로 크롤링됩니다:

```yaml
name: Daily Scraping
on:
  schedule:
    - cron: '0 */6 * * *'  # 6시간마다 실행
  workflow_dispatch:  # 수동 실행 가능

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install playwright beautifulsoup4 lxml
          playwright install chromium
      - name: Run scraper
        run: python wconcept_scraper_v2.py
```

---

## 💡 프로 팁

### 커스텀 도메인 연결
Cloudflare Pages → Custom domains → 도메인 추가

### 무료 SSL/HTTPS
Cloudflare가 자동 제공 (별도 설정 불필요)

### 성능 모니터링
- Cloudflare Analytics에서 방문자 통계 확인
- Render/Railway 대시보드에서 API 성능 모니터링

### 비용 관리
- **Cloudflare Pages**: 무료 (월 500 빌드까지)
- **Render.com**: 무료 tier (750시간/월, 인스턴스 1개)
- **Railway**: 무료 tier ($5 credit/월)

---

## 📚 상세 가이드

더 자세한 내용은 아래 문서를 참고하세요:
- [CLOUDFLARE_DEPLOY.md](./CLOUDFLARE_DEPLOY.md) - 상세 배포 가이드
- [README.md](./README.md) - 프로젝트 전체 설명

---

## 🆘 문제 해결

### Cloudflare 빌드 실패
- 빌드 로그에서 에러 확인
- `Build command`와 `Build output directory` 재확인

### API 연결 실패 (CORS)
- API 서버가 정상 실행 중인지 확인
- `api.py`의 CORS 설정 확인 (이미 설정됨)

### 데이터가 표시되지 않음
- Cloudflare 환경 변수 `VITE_API_BASE_URL` 확인
- 브라우저 콘솔에서 API 요청 확인
- API URL 끝에 `/` 제거 확인

---

## 🎉 배포 완료!

**축하합니다!** W컨셉 베스트 제품 추적 시스템이 성공적으로 배포되었습니다!

### 다음 단계
1. ✅ 대시보드 URL 공유
2. ✅ API 서버 모니터링
3. ✅ 정기적인 데이터 수집 설정
4. ✅ 사용자 피드백 수집

---

**질문이나 문제가 있으면 GitHub Issues에 등록해주세요!**

Repository: https://github.com/happypororo/W-Best-Tracker
