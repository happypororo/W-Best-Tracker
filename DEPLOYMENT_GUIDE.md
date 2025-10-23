# 🚀 W Concept 베스트 제품 추적 시스템 - 배포 가이드

## 📊 현재 상태

✅ **GitHub 저장소**: Private (본인만 볼 수 있음)
✅ **프론트엔드 빌드**: 완료 (dashboard/dist/)
✅ **API 서버**: FastAPI (Python)
✅ **데이터베이스**: SQLite (1,600개 제품 데이터 포함)

---

## 🌐 Cloudflare Pages 배포 방법

### 방법 1: Cloudflare Dashboard 사용 (추천)

#### Step 1: Cloudflare 대시보드 접속
1. https://dash.cloudflare.com/ 로그인
2. 좌측 메뉴에서 **"Workers & Pages"** 클릭
3. **"Create application"** 버튼 클릭
4. **"Pages"** 탭 선택
5. **"Connect to Git"** 클릭

#### Step 2: GitHub 연결
1. **GitHub 계정 연결** (처음이면 승인 필요)
2. 저장소 선택: **`happypororo/W-Best-Tracker`**
3. 브랜치 선택: **`genspark_ai_developer`**

#### Step 3: 빌드 설정

```
프로젝트 이름: w-best-tracker (또는 원하는 이름)
프로덕션 브랜치: genspark_ai_developer

빌드 설정:
- Framework preset: Vite
- Build command: cd dashboard && npm install && npm run build
- Build output directory: dashboard/dist
- Root directory: (비워두기)
- Node version: 18 이상
```

#### Step 4: 환경 변수 설정 (선택사항)

현재는 API가 샌드박스에서 실행 중이므로, 프로덕션 API URL이 준비되면 추가:

```
변수 이름: VITE_API_BASE_URL
값: https://your-api-server-url.com
```

지금은 설정하지 않아도 됩니다 (코드에 기본값이 있음).

#### Step 5: 배포 시작
1. **"Save and Deploy"** 클릭
2. 빌드 진행 상황 확인 (약 2-3분 소요)
3. 배포 완료 후 URL 확인

---

### 방법 2: Wrangler CLI 사용

터미널에서 직접 배포하려면:

```bash
# 1. Cloudflare 로그인
npx wrangler login

# 2. 배포 (dashboard 디렉토리에서)
cd /home/user/webapp/dashboard
npx wrangler pages deploy dist --project-name=w-best-tracker
```

---

## 🔐 접근 권한 설정

### GitHub Private 저장소
- ✅ 현재 저장소는 **Private**으로 설정됨
- 본인(happypororo)만 저장소에 접근 가능
- 다른 사람은 코드를 볼 수 없음

### Cloudflare Pages 접근 제한

배포 후 Cloudflare에서 추가 보안 설정 가능:

1. **Cloudflare Access 사용** (유료 플랜)
   - 특정 이메일만 접근 허용
   - 비밀번호 보호

2. **무료 옵션**:
   - 배포된 URL을 공유하지 않으면 찾기 어려움
   - URL에 랜덤 문자열 포함됨 (예: w-best-tracker-abc123.pages.dev)

---

## 🔧 API 서버 배포 (별도 필요)

현재 API는 샌드박스에서 실행 중입니다. 프로덕션 배포 옵션:

### 옵션 1: Railway (추천 - 무료 티어)
```bash
# Railway CLI 설치
npm install -g railway

# 프로젝트 초기화
cd /home/user/webapp
railway login
railway init
railway up

# 환경 변수 설정
railway variables set DATABASE_PATH=/data/wconcept_tracking.db
```

### 옵션 2: Render (무료 티어)
1. https://render.com 가입
2. "New Web Service" 생성
3. GitHub 저장소 연결
4. 설정:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api:app --host 0.0.0.0 --port 8000`

### 옵션 3: Fly.io (무료 티어)
```bash
# Fly CLI 설치
curl -L https://fly.io/install.sh | sh

# 앱 생성 및 배포
cd /home/user/webapp
fly launch
fly deploy
```

---

## 📋 배포 체크리스트

### 프론트엔드 (Cloudflare Pages)
- [x] GitHub 저장소 Private 설정 확인
- [x] 대시보드 빌드 성공
- [ ] Cloudflare Pages 프로젝트 생성
- [ ] GitHub 저장소 연결
- [ ] 빌드 설정 완료
- [ ] 배포 완료
- [ ] 배포된 URL 테스트

### 백엔드 (API 서버)
- [ ] 프로덕션 서버 선택 (Railway/Render/Fly.io)
- [ ] API 배포 완료
- [ ] 데이터베이스 마이그레이션
- [ ] 크롤링 스케줄러 설정
- [ ] API URL을 프론트엔드에 설정

---

## 🌐 예상 배포 URL

### 프론트엔드
- Cloudflare Pages: `https://w-best-tracker.pages.dev`
- 커스텀 도메인 연결 가능

### 백엔드
- Railway: `https://w-best-tracker-api.railway.app`
- Render: `https://w-best-tracker-api.onrender.com`
- Fly.io: `https://w-best-tracker-api.fly.dev`

---

## 🔄 자동 배포 설정

배포 후 GitHub에 푸시하면 자동으로 배포됩니다:

```bash
# 코드 수정 후
git add .
git commit -m "Update feature"
git push origin genspark_ai_developer

# Cloudflare Pages가 자동으로 새 버전 배포
```

---

## 💡 추가 팁

1. **빌드 확인**: 로컬에서 빌드가 성공하는지 먼저 테스트
   ```bash
   cd dashboard
   npm run build
   npm run preview  # 빌드 결과 미리보기
   ```

2. **환경 변수**: 프로덕션 API URL을 환경 변수로 관리

3. **커스텀 도메인**: Cloudflare에서 무료로 커스텀 도메인 연결 가능

4. **HTTPS**: Cloudflare Pages는 자동으로 HTTPS 제공

5. **롤백**: Cloudflare Dashboard에서 이전 배포 버전으로 쉽게 롤백 가능

---

## 📞 문제 해결

### 빌드 실패
- Node.js 버전 확인 (18 이상 필요)
- package.json 의존성 확인
- 빌드 로그에서 에러 메시지 확인

### API 연결 안 됨
- CORS 설정 확인 (api.py의 CORS 미들웨어)
- API URL 환경 변수 확인
- 브라우저 개발자 도구의 Network 탭 확인

### 데이터 없음
- API 서버가 실행 중인지 확인
- 데이터베이스 파일이 있는지 확인
- 크롤링이 정상 작동하는지 확인

---

## 📚 참고 문서

- [Cloudflare Pages 문서](https://developers.cloudflare.com/pages/)
- [Vite 배포 가이드](https://vitejs.dev/guide/static-deploy.html)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/)
- [Railway 문서](https://docs.railway.app/)
- [Render 문서](https://render.com/docs)

---

## ✨ 배포 완료 후

배포가 완료되면 다음 정보를 확인하세요:

1. **프론트엔드 URL**: https://[your-project].pages.dev
2. **API URL**: (별도 배포 필요)
3. **GitHub 저장소**: https://github.com/happypororo/W-Best-Tracker (Private)
4. **Pull Request**: https://github.com/happypororo/W-Best-Tracker/pull/1

---

**배포 날짜**: 2025-10-24
**버전**: 1.0.0
**프로젝트 이름**: W Concept 베스트 제품 추적 시스템
