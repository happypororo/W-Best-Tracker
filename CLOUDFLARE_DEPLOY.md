# Cloudflare Pages 배포 가이드

## 📋 사전 준비

1. **Cloudflare 계정** - https://dash.cloudflare.com/ 에서 가입
2. **GitHub 저장소** - 코드가 푸시된 GitHub 저장소

---

## 🚀 1단계: 프론트엔드 (대시보드) 배포

### A. Cloudflare Pages 프로젝트 생성

1. **Cloudflare Dashboard 접속**
   - https://dash.cloudflare.com/ 로그인
   - 좌측 메뉴에서 `Workers & Pages` 클릭

2. **새 프로젝트 생성**
   - `Create application` 버튼 클릭
   - `Pages` 탭 선택
   - `Connect to Git` 클릭

3. **GitHub 저장소 연결**
   - GitHub 계정 연결 (처음이라면)
   - 저장소 선택
   - `Begin setup` 클릭

4. **빌드 설정**
   ```
   Project name: wconcept-dashboard
   Production branch: main (또는 genspark_ai_developer)
   Framework preset: Vite
   Build command: cd dashboard && npm install && npm run build
   Build output directory: dashboard/dist
   ```

5. **환경 변수 설정**
   - `Environment variables` 섹션에서 `Add variable` 클릭
   ```
   Variable name: VITE_API_BASE_URL
   Value: YOUR_API_SERVER_URL (나중에 API 서버 배포 후 업데이트)
   ```

6. **배포 시작**
   - `Save and Deploy` 클릭
   - 빌드 완료 대기 (약 2-3분)

7. **배포 완료**
   - 배포 완료 후 URL 확인 (예: `https://wconcept-dashboard.pages.dev`)

---

## 🔧 2단계: 백엔드 (API 서버) 배포 옵션

백엔드 API 서버는 여러 방법으로 배포할 수 있습니다:

### 옵션 A: Render.com (추천 - 무료)

1. **Render.com 가입**
   - https://render.com/ 계정 생성

2. **New Web Service 생성**
   - Dashboard > `New +` > `Web Service`
   - GitHub 저장소 연결

3. **설정**
   ```
   Name: wconcept-api
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn api:app --host 0.0.0.0 --port $PORT
   ```

4. **환경 변수 설정**
   ```
   DB_PATH: /opt/render/project/src/wconcept_tracking.db
   ```

5. **배포 완료**
   - URL 확인 (예: `https://wconcept-api.onrender.com`)

### 옵션 B: Railway.app (무료 tier)

1. **Railway 가입**
   - https://railway.app/ 계정 생성

2. **New Project**
   - `Deploy from GitHub repo` 선택

3. **설정**
   - Automatically detected as Python project
   - Start Command: `uvicorn api:app --host 0.0.0.0 --port $PORT`

4. **도메인 생성**
   - Settings > `Generate Domain`

### 옵션 C: Fly.io (추천 - 성능)

1. **Fly.io 설치**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **로그인**
   ```bash
   flyctl auth login
   ```

3. **앱 생성**
   ```bash
   cd /home/user/webapp
   flyctl launch --name wconcept-api
   ```

4. **배포**
   ```bash
   flyctl deploy
   ```

### 옵션 D: 자체 VPS (고급)

- DigitalOcean, Linode, AWS EC2 등
- Docker 컨테이너 사용 추천
- Nginx + Gunicorn/Uvicorn 구성

---

## 🔗 3단계: 프론트엔드와 백엔드 연결

1. **API 서버 URL 확인**
   - 배포된 백엔드 API URL 복사

2. **Cloudflare Pages 환경 변수 업데이트**
   - Cloudflare Dashboard > Pages > wconcept-dashboard
   - Settings > Environment variables
   - `VITE_API_BASE_URL` 값을 실제 API URL로 업데이트
   ```
   예: https://wconcept-api.onrender.com
   ```

3. **재배포**
   - Settings > Builds & deployments
   - `Retry deployment` 클릭

---

## ✅ 4단계: 동작 확인

1. **프론트엔드 접속**
   - Cloudflare Pages URL 접속
   - 대시보드가 정상적으로 로드되는지 확인

2. **API 연결 확인**
   - 브라우저 개발자 도구 (F12) > Console
   - Network 탭에서 API 요청 확인
   - 데이터가 정상적으로 로드되는지 확인

3. **모든 기능 테스트**
   - TOP 10 제품 표시
   - 카테고리 필터링
   - 브랜드 통계 차트
   - 순위 동향 차트

---

## 📊 빠른 배포 (Cloudflare Pages만)

GitHub에 푸시된 상태에서:

```bash
# 1. Cloudflare에서 Git 연결
# 2. 빌드 설정:
Build command: cd dashboard && npm install && npm run build
Build output: dashboard/dist

# 3. 환경 변수:
VITE_API_BASE_URL=https://8000-is73bj77dclhgdm3vfpjp-2e77fc33.sandbox.novita.ai

# 4. Deploy!
```

⚠️ **주의**: 샌드박스 API URL은 임시입니다. 프로덕션에서는 반드시 영구적인 API 서버를 배포하세요.

---

## 🔄 자동 배포 (CI/CD)

GitHub에 푸시하면 자동으로 Cloudflare Pages가 빌드/배포합니다:

```bash
git add .
git commit -m "Update dashboard"
git push origin main
```

Cloudflare가 자동으로:
1. 코드 변경 감지
2. 빌드 실행
3. 배포 완료

---

## 💡 팁

### 커스텀 도메인 연결

1. Cloudflare Pages > Custom domains
2. `Set up a custom domain` 클릭
3. 도메인 입력 및 DNS 설정

### HTTPS 자동 적용

- Cloudflare Pages는 자동으로 HTTPS 제공
- 별도 설정 불필요

### 빌드 로그 확인

- Deployments 탭에서 빌드 로그 확인 가능
- 에러 발생 시 로그에서 원인 파악

---

## 🆘 문제 해결

### 빌드 실패

```bash
# 로컬에서 빌드 테스트
cd dashboard
npm install
npm run build
```

### API 연결 실패

- 브라우저 콘솔에서 CORS 에러 확인
- API 서버에서 CORS 설정 확인 (api.py의 CORSMiddleware)

### 환경 변수 미적용

- Cloudflare Pages에서 환경 변수 재확인
- 재배포 필요 (환경 변수 변경 후)

---

## 📚 참고 자료

- [Cloudflare Pages 문서](https://developers.cloudflare.com/pages/)
- [Vite 배포 가이드](https://vitejs.dev/guide/static-deploy.html)
- [Render.com 문서](https://render.com/docs)
- [Railway 문서](https://docs.railway.app/)

---

**배포 완료 후 이 저장소의 README.md를 업데이트하여 실제 URL을 공유하세요!** 🎉
