# Cloudflare Pages 배포 가이드

## 📋 개요

이 프로젝트를 Cloudflare Pages에 배포하는 방법을 설명합니다.

## 🚀 배포 단계

### 1. GitHub 저장소 준비

```bash
# 변경사항 커밋
git add .
git commit -m "Add Cloudflare Pages deployment setup"
git push origin genspark_ai_developer
```

### 2. Cloudflare Pages 설정

1. **Cloudflare 대시보드 접속**
   - https://dash.cloudflare.com/ 로그인

2. **Pages 프로젝트 생성**
   - 좌측 메뉴에서 "Workers & Pages" 클릭
   - "Create application" 버튼 클릭
   - "Pages" 탭 선택
   - "Connect to Git" 클릭

3. **GitHub 저장소 연결**
   - GitHub 계정 연결
   - 이 저장소 선택
   - `genspark_ai_developer` 브랜치 선택

4. **빌드 설정**
   ```
   Framework preset: Vite
   Build command: cd dashboard && npm install && npm run build
   Build output directory: dashboard/dist
   Root directory: /
   ```

5. **환경 변수 설정**
   - "Environment variables" 섹션에서 추가:
     ```
     VITE_API_BASE_URL=https://your-api-server-url.com
     ```
   - API 서버 URL을 실제 URL로 변경

6. **배포 시작**
   - "Save and Deploy" 클릭
   - 빌드 및 배포 완료 대기 (약 2-3분)

## 🔧 API 서버 배포

대시보드는 Cloudflare Pages에, API 서버는 별도 호스팅이 필요합니다.

### 옵션 1: Cloudflare Workers (추천)

API를 Cloudflare Workers로 배포하면 완전한 서버리스 솔루션이 됩니다.

```bash
# Wrangler 설치
npm install -g wrangler

# Workers 프로젝트 생성
cd api-worker
wrangler init

# 배포
wrangler deploy
```

### 옵션 2: 다른 클라우드 서비스

- **Heroku**: Python 앱 배포 가능
- **Railway**: 간단한 배포
- **Render**: 무료 티어 제공
- **AWS Lambda**: 서버리스
- **Google Cloud Run**: 컨테이너 기반

## 📊 데이터베이스

프로덕션 환경에서는 SQLite 대신 다음 옵션 고려:

1. **Cloudflare D1** (추천)
   - Cloudflare의 SQLite 기반 데이터베이스
   - Workers와 통합 용이

2. **Supabase**
   - PostgreSQL 기반
   - 무료 티어 제공

3. **PlanetScale**
   - MySQL 호환
   - 서버리스

## 🔄 자동 배포

GitHub에 푸시할 때마다 자동으로 배포됩니다:

```bash
# 코드 수정 후
git add .
git commit -m "Update feature"
git push origin genspark_ai_developer

# Cloudflare Pages가 자동으로 빌드 및 배포
```

## 🌐 커스텀 도메인

Cloudflare Pages에서 커스텀 도메인 설정:

1. Pages 프로젝트 설정 > Custom domains
2. 도메인 추가
3. DNS 레코드 설정
4. SSL/TLS 자동 설정

## 📝 환경별 설정

### 개발 환경
```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000
```

### 프로덕션 환경
```bash
# Cloudflare Pages 환경 변수로 설정
VITE_API_BASE_URL=https://api.yourdomain.com
```

## 🔍 트러블슈팅

### 빌드 실패
- Node.js 버전 확인 (18 이상 권장)
- package.json 의존성 확인
- 빌드 로그에서 에러 확인

### API 연결 실패
- CORS 설정 확인
- API URL 환경 변수 확인
- 네트워크 탭에서 요청 확인

### 데이터 로딩 안 됨
- API 서버가 실행 중인지 확인
- 데이터베이스에 데이터가 있는지 확인
- 브라우저 콘솔 에러 확인

## 📚 추가 리소스

- [Cloudflare Pages 문서](https://developers.cloudflare.com/pages/)
- [Vite 배포 가이드](https://vitejs.dev/guide/static-deploy.html)
- [Cloudflare Workers 문서](https://developers.cloudflare.com/workers/)
- [Cloudflare D1 문서](https://developers.cloudflare.com/d1/)

## 💡 팁

1. **프리뷰 배포**: Pull Request마다 자동 프리뷰 생성
2. **빌드 로그**: 상세한 빌드 로그 확인 가능
3. **롤백**: 이전 배포로 즉시 롤백 가능
4. **Analytics**: 페이지 뷰 및 성능 모니터링

