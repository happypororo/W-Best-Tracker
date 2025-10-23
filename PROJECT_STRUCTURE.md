# 📁 프로젝트 구조

```
wconcept-tracker/
│
├── 📄 README.md                          # 프로젝트 개요
├── 📄 QUICK_SUMMARY.md                   # 빠른 요약
├── 📄 WCONCEPT_FEASIBILITY_REPORT.md    # 상세 가능성 분석
├── 📄 PROJECT_STRUCTURE.md               # 이 파일
│
├── 📄 requirements.txt                   # Python 패키지 목록
├── 📄 .env.example                       # 환경 변수 템플릿
├── 📄 .gitignore                         # Git 무시 파일
│
├── 🧪 test_wconcept_scraper.py          # 기본 크롤링 테스트
├── 🧪 test_selenium_scraper.py          # Selenium 테스트
│
├── 📂 src/                               # 소스 코드
│   ├── 📄 __init__.py
│   │
│   ├── 📂 scraper/                       # 크롤링 모듈
│   │   ├── 📄 __init__.py
│   │   ├── 📄 wconcept_scraper.py       # 메인 크롤러
│   │   ├── 📄 driver_setup.py           # Selenium 드라이버 설정
│   │   └── 📄 parsers.py                # HTML 파싱 로직
│   │
│   ├── 📂 database/                      # 데이터베이스 모듈
│   │   ├── 📄 __init__.py
│   │   ├── 📄 models.py                 # SQLAlchemy 모델
│   │   ├── 📄 connection.py             # DB 연결 설정
│   │   ├── 📄 crud.py                   # CRUD 작업
│   │   └── 📄 queries.py                # 복잡한 쿼리
│   │
│   ├── 📂 api/                           # REST API
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main.py                   # FastAPI 앱
│   │   ├── 📄 routes.py                 # API 라우트
│   │   ├── 📄 schemas.py                # Pydantic 스키마
│   │   └── 📄 dependencies.py           # 의존성
│   │
│   ├── 📂 scheduler/                     # 스케줄러
│   │   ├── 📄 __init__.py
│   │   ├── 📄 scheduler.py              # APScheduler 설정
│   │   └── 📄 jobs.py                   # 스케줄 작업
│   │
│   └── 📂 utils/                         # 유틸리티
│       ├── 📄 __init__.py
│       ├── 📄 logger.py                 # 로깅 설정
│       ├── 📄 config.py                 # 설정 관리
│       └── 📄 helpers.py                # 헬퍼 함수
│
├── 📂 tests/                             # 테스트 코드
│   ├── 📄 __init__.py
│   ├── 📄 test_scraper.py               # 크롤러 테스트
│   ├── 📄 test_database.py              # DB 테스트
│   └── 📄 test_api.py                   # API 테스트
│
├── 📂 data/                              # 데이터 저장
│   ├── 📄 .gitkeep
│   └── 🗄️ wconcept.db                   # SQLite DB (개발용)
│
├── 📂 logs/                              # 로그 파일
│   ├── 📄 .gitkeep
│   └── 📄 app.log                       # 애플리케이션 로그
│
├── 📂 frontend/                          # 프론트엔드 (선택적)
│   ├── 📂 public/
│   ├── 📂 src/
│   │   ├── 📂 components/
│   │   ├── 📂 pages/
│   │   ├── 📂 services/
│   │   └── 📄 App.js
│   ├── 📄 package.json
│   └── 📄 README.md
│
├── 📂 docker/                            # Docker 설정
│   ├── 📄 Dockerfile
│   └── 📄 docker-compose.yml
│
└── 📂 docs/                              # 문서
    ├── 📄 API.md                        # API 문서
    ├── 📄 DATABASE.md                   # DB 스키마 문서
    └── 📄 DEPLOYMENT.md                 # 배포 가이드
```

## 📋 주요 파일 설명

### 핵심 소스 코드

#### 1. **src/scraper/wconcept_scraper.py**
W컨셉 베스트 상품 크롤링의 핵심 로직
```python
class WConceptScraper:
    def scrape_best_products(self, limit=200):
        # 200개 상품 수집
        pass
```

#### 2. **src/database/models.py**
데이터베이스 테이블 정의
```python
class Product(Base):
    # 상품 정보
    
class Ranking(Base):
    # 순위 히스토리
```

#### 3. **src/api/main.py**
FastAPI 애플리케이션
```python
@app.get("/api/rankings/latest")
async def get_latest_rankings():
    # 최신 랭킹 반환
```

#### 4. **src/scheduler/scheduler.py**
주기적 크롤링 실행
```python
scheduler.add_job(
    func=scrape_job,
    trigger="interval",
    hours=1
)
```

### 설정 파일

#### **.env.example**
환경 변수 템플릿 (실제 사용 시 `.env`로 복사)

#### **requirements.txt**
필요한 Python 패키지 목록

### 테스트 파일

#### **test_wconcept_scraper.py**
기본 HTTP 요청 테스트 및 페이지 구조 분석

#### **test_selenium_scraper.py**
Selenium 기반 크롤링 테스트

## 🚀 시작하기

### 1. 환경 설정
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 수정
```

### 2. 데이터베이스 초기화
```bash
# SQLite (개발용)
python -c "from src.database.models import init_db; init_db()"

# PostgreSQL (프로덕션)
# .env에서 DATABASE_URL 설정 후
alembic upgrade head
```

### 3. 크롤링 테스트
```bash
# 기본 테스트
python test_wconcept_scraper.py

# Selenium 테스트
python test_selenium_scraper.py
```

### 4. API 서버 실행
```bash
cd src/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 스케줄러 시작
```bash
python -m src.scheduler.scheduler
```

## 📊 데이터 흐름

```
[스케줄러] 
    ↓ (1시간마다)
[크롤러] → W컨셉 접속
    ↓
[파서] → HTML 파싱
    ↓
[데이터베이스] → 저장
    ↓
[API] → 데이터 제공
    ↓
[프론트엔드] → 시각화
```

## 🔧 개발 워크플로우

### 단계별 개발 순서

1. **크롤러 개발** (src/scraper/)
   - Selenium 설정
   - 페이지 로딩 및 파싱
   - 데이터 추출

2. **데이터베이스 설계** (src/database/)
   - 모델 정의
   - 마이그레이션
   - CRUD 작업

3. **스케줄러 구현** (src/scheduler/)
   - APScheduler 설정
   - 작업 정의
   - 에러 핸들링

4. **API 개발** (src/api/)
   - 엔드포인트 정의
   - 데이터 조회 로직
   - 문서화

5. **프론트엔드 개발** (frontend/)
   - React 컴포넌트
   - 차트 라이브러리 통합
   - UI/UX 디자인

6. **테스트 및 배포**
   - 단위 테스트
   - 통합 테스트
   - Docker 컨테이너화

## 📝 다음 할 일

- [ ] 실제 W컨셉 페이지 HTML 구조 분석
- [ ] 정확한 CSS 셀렉터 찾기
- [ ] 크롤러 프로토타입 구현
- [ ] 데이터베이스 스키마 확정
- [ ] API 엔드포인트 설계
- [ ] 프론트엔드 모형 디자인

## 💡 유용한 명령어

```bash
# 전체 테스트 실행
pytest tests/

# 코드 포맷팅
black src/
isort src/

# 타입 체크
mypy src/

# 린팅
flake8 src/

# API 문서 확인
# http://localhost:8000/docs
```

## 📚 참고 자료

- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Selenium 문서](https://www.selenium.dev/documentation/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
- [APScheduler 문서](https://apscheduler.readthedocs.io/)

---

**프로젝트 구조가 준비되었습니다!** 🎉
