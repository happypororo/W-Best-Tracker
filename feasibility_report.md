# W컨셉 베스트 상품 순위 트래킹 시스템 - 구현 가능성 분석 보고서

## 📋 프로젝트 개요

**목표**: W컨셉 베스트 상품 1~200위의 순위 변화를 시간 단위로 트래킹하는 시스템 구축

**분석 날짜**: 2025-10-23

---

## ✅ 요구사항 분석 및 구현 가능성

### 1. Top 200개의 브랜드 & 제품 정보 수집
**상태**: ✅ **구현 가능**

#### 확인된 사항:
- W컨셉 사이트는 봇 차단 기능 사용 중
- 기본 HTTP 요청 시: "정상적인 조회형식이 아닙니다" 메시지 반환
- **해결 방법**: Selenium을 사용한 브라우저 자동화 필요

#### 수집 가능한 데이터:
- ✅ 상품명
- ✅ 브랜드명
- ✅ 가격 (정가, 할인가)
- ✅ 상품 이미지 URL
- ✅ 상품 상세 페이지 URL
- ✅ 할인율
- ✅ 순위 정보
- ✅ 수집 시간 (타임스탬프)

#### 구현 방식:
```python
# Selenium + BeautifulSoup 조합
1. Selenium으로 페이지 렌더링 (JavaScript 실행)
2. 페이지 로딩 대기 (동적 컨텐츠 로드)
3. 필요시 스크롤 다운 (무한 스크롤 처리)
4. BeautifulSoup으로 HTML 파싱
5. 상품 정보 추출 및 정규화
```

**예상 소요 시간**: 200개 상품 수집에 약 30~60초

---

### 2. 브랜드별 제품 개수 집계
**상태**: ✅ **구현 가능**

#### 구현 방식:
수집된 데이터를 데이터베이스에 저장 후 집계 쿼리 실행

```sql
-- 특정 시점의 브랜드별 제품 수
SELECT 
    brand_name,
    COUNT(*) as product_count,
    AVG(ranking) as avg_ranking,
    MIN(ranking) as best_ranking
FROM products
WHERE collected_at = '2025-10-23 10:00:00'
GROUP BY brand_name
ORDER BY product_count DESC;
```

#### 제공 가능한 분석:
- ✅ 브랜드별 순위권 진입 제품 수
- ✅ 브랜드별 평균 순위
- ✅ 브랜드별 최고 순위
- ✅ 시간대별 브랜드 점유율 변화
- ✅ 신규 진입/탈락 브랜드 추적

---

### 3. 가격 변화 추적
**상태**: ✅ **구현 가능**

#### 추적 가능한 가격 정보:
- ✅ 정가 (original_price)
- ✅ 판매가 (sale_price)
- ✅ 할인율 (discount_rate)
- ✅ 가격 변동 이력
- ✅ 가격 변동 빈도

#### 분석 가능한 메트릭:
```python
# 가격 변화 분석
1. 가격 인상/인하 감지
2. 할인율 변화 추적
3. 평균 할인율 계산
4. 가격 변동 패턴 분석 (요일별, 시간대별)
5. 프로모션 기간 감지
```

#### 데이터 저장 구조:
```sql
-- 시계열 데이터로 저장
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(100),
    collected_at TIMESTAMP,
    original_price INTEGER,
    sale_price INTEGER,
    discount_rate DECIMAL(5,2),
    price_changed BOOLEAN
);
```

---

### 4. 정해진 시간마다 반복 실행
**상태**: ✅ **구현 가능**

#### 권장 스케줄링 방법:

##### 방법 1: APScheduler (추천)
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

# 매 시간마다 실행
scheduler.add_job(scrape_wconcept, 'interval', hours=1)

# 특정 시간에 실행 (매일 9시, 12시, 18시, 21시)
scheduler.add_job(scrape_wconcept, 'cron', hour='9,12,18,21')

scheduler.start()
```

##### 방법 2: Celery + Redis
```python
# 분산 처리 및 대규모 스케줄링에 적합
from celery import Celery

app = Celery('wconcept_tracker')

@app.task
def scrape_wconcept_task():
    # 크롤링 로직
    pass

# Celery Beat로 스케줄링
app.conf.beat_schedule = {
    'scrape-every-hour': {
        'task': 'scrape_wconcept_task',
        'schedule': 3600.0,  # 1시간
    },
}
```

##### 방법 3: Cron Job (Linux)
```bash
# crontab -e
# 매 시간마다 실행
0 * * * * cd /home/user/webapp && python scraper.py

# 매일 특정 시간에 실행
0 9,12,18,21 * * * cd /home/user/webapp && python scraper.py
```

#### 실행 주기 권장사항:
- **최소 간격**: 30분 (서버 부하 고려)
- **권장 간격**: 1시간
- **최적 시간대**: 
  - 09:00 (오전 쇼핑 시작)
  - 12:00 (점심 시간)
  - 18:00 (퇴근 시간)
  - 21:00 (저녁 쇼핑 피크)

---

## 🏗️ 시스템 아키텍처 제안

### 기술 스택

#### Backend
- **언어**: Python 3.10+
- **웹 프레임워크**: FastAPI
- **크롤링**: Selenium + BeautifulSoup4
- **데이터베이스**: PostgreSQL (또는 SQLite)
- **스케줄러**: APScheduler
- **캐싱**: Redis (선택사항)

#### Frontend
- **프레임워크**: React 18 + TypeScript
- **차트 라이브러리**: Chart.js 또는 Recharts
- **UI 라이브러리**: Material-UI 또는 Ant Design
- **상태 관리**: Zustand 또는 Redux Toolkit

#### DevOps
- **컨테이너**: Docker + Docker Compose
- **웹서버**: Nginx
- **프로세스 관리**: Supervisor 또는 PM2

### 시스템 구조도

```
┌─────────────────────────────────────────────────────────┐
│                     사용자 브라우저                        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  Nginx (Reverse Proxy)                   │
└───────────┬─────────────────────────┬───────────────────┘
            │                         │
            ▼                         ▼
┌──────────────────────┐    ┌──────────────────────┐
│   React Frontend     │    │   FastAPI Backend    │
│   (Port 3000)        │    │   (Port 8000)        │
└──────────────────────┘    └──────────┬───────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
         ┌─────────────────┐  ┌──────────────┐  ┌──────────────┐
         │   PostgreSQL    │  │  APScheduler │  │   Selenium   │
         │   (Database)    │  │  (Scheduler) │  │  (Scraper)   │
         └─────────────────┘  └──────────────┘  └──────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │  W컨셉 웹사이트  │
                              └─────────────────┘
```

---

## 📊 데이터베이스 스키마 설계

```sql
-- 제품 기본 정보
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(100) UNIQUE NOT NULL,
    product_name VARCHAR(500) NOT NULL,
    brand_name VARCHAR(200) NOT NULL,
    product_url TEXT,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 순위 및 가격 이력 (시계열 데이터)
CREATE TABLE ranking_history (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(100) REFERENCES products(product_id),
    ranking INTEGER NOT NULL,
    original_price INTEGER,
    sale_price INTEGER,
    discount_rate DECIMAL(5,2),
    collected_at TIMESTAMP NOT NULL,
    INDEX idx_collected_at (collected_at),
    INDEX idx_product_time (product_id, collected_at)
);

-- 브랜드 정보
CREATE TABLE brands (
    id SERIAL PRIMARY KEY,
    brand_name VARCHAR(200) UNIQUE NOT NULL,
    brand_url TEXT,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 순위 변동 로그
CREATE TABLE ranking_changes (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(100) REFERENCES products(product_id),
    previous_ranking INTEGER,
    current_ranking INTEGER,
    change_amount INTEGER,  -- 양수: 상승, 음수: 하락
    changed_at TIMESTAMP NOT NULL
);

-- 가격 변동 로그
CREATE TABLE price_changes (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(100) REFERENCES products(product_id),
    previous_price INTEGER,
    current_price INTEGER,
    change_amount INTEGER,
    change_percentage DECIMAL(5,2),
    changed_at TIMESTAMP NOT NULL
);

-- 크롤링 작업 로그
CREATE TABLE scraping_logs (
    id SERIAL PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR(50),  -- 'success', 'failed', 'partial'
    products_collected INTEGER,
    error_message TEXT,
    execution_time_seconds INTEGER
);
```

---

## 🔍 주요 기능 명세

### 1. 데이터 수집 모듈

```python
class WConceptScraper:
    """W컨셉 베스트 상품 크롤러"""
    
    def scrape_best_products(self, limit=200):
        """
        베스트 상품 수집
        
        Returns:
            List[Dict]: 상품 정보 리스트
        """
        pass
    
    def extract_product_info(self, element):
        """
        개별 상품 정보 추출
        
        Returns:
            Dict: {
                'product_id': str,
                'product_name': str,
                'brand_name': str,
                'ranking': int,
                'original_price': int,
                'sale_price': int,
                'discount_rate': float,
                'product_url': str,
                'image_url': str
            }
        """
        pass
```

### 2. 데이터 분석 API

```python
# FastAPI 엔드포인트

@app.get("/api/products/current")
async def get_current_rankings(limit: int = 200):
    """현재 순위 조회"""
    pass

@app.get("/api/products/{product_id}/history")
async def get_product_history(product_id: str, days: int = 7):
    """특정 상품의 순위/가격 변동 이력"""
    pass

@app.get("/api/brands/stats")
async def get_brand_statistics(time_range: str = "24h"):
    """브랜드별 통계"""
    pass

@app.get("/api/analysis/price-changes")
async def get_price_changes(hours: int = 24):
    """가격 변동 분석"""
    pass

@app.get("/api/analysis/ranking-movers")
async def get_ranking_movers(change_type: str = "up"):
    """순위 급상승/급하락 상품"""
    pass
```

### 3. 대시보드 기능

#### 메인 대시보드
- 📊 현재 Top 200 상품 목록
- 📈 순위 변동 차트
- 💰 가격 변동 알림
- 🏷️ 브랜드별 점유율

#### 상품 상세 페이지
- 📉 순위 변동 그래프 (시계열)
- 💵 가격 변동 히스토리
- 🔔 가격 알림 설정
- 📊 경쟁 상품 비교

#### 브랜드 분석 페이지
- 🏢 브랜드별 제품 수
- 📊 평균 순위 추이
- 💰 평균 가격대 분석
- 📈 점유율 변화 그래프

#### 분석 대시보드
- 🚀 순위 급상승 TOP 20
- 📉 순위 급하락 TOP 20
- 💰 최근 가격 변동 상품
- 🆕 신규 진입 상품
- 👋 순위권 탈락 상품

---

## ⚠️ 구현 시 주의사항

### 1. 법적/윤리적 고려사항
- ✅ **robots.txt 준수**: W컨셉의 크롤링 정책 확인 필수
- ✅ **요청 빈도 제한**: 서버에 과부하를 주지 않도록 적절한 딜레이 설정
- ✅ **이용약관 검토**: 데이터 수집 및 사용에 대한 법적 검토 필요
- ⚠️ **개인정보 보호**: 사용자 리뷰 등 개인정보는 수집하지 않음

### 2. 기술적 고려사항

#### 안정성
```python
# 재시도 로직 구현
import tenacity

@tenacity.retry(
    wait=tenacity.wait_exponential(min=1, max=60),
    stop=tenacity.stop_after_attempt(3),
    retry=tenacity.retry_if_exception_type(Exception)
)
def scrape_with_retry():
    """재시도 로직이 포함된 크롤링"""
    pass
```

#### 에러 처리
- 네트워크 오류 처리
- 페이지 구조 변경 감지
- 데이터 유효성 검증
- 로깅 및 모니터링

#### 성능 최적화
- 데이터베이스 인덱싱
- 쿼리 최적화
- 캐싱 전략 (Redis)
- 비동기 처리 (asyncio)

### 3. 운영 고려사항

#### 모니터링
```python
# 크롤링 성공률 모니터링
# 데이터 품질 체크
# 시스템 리소스 모니터링
# 에러 알림 설정
```

#### 백업 및 복구
- 정기적인 데이터베이스 백업
- 크롤링 실패 시 복구 전략
- 데이터 정합성 검증

---

## 📅 구현 로드맵

### Phase 1: 기본 크롤링 (1주)
- [x] W컨셉 페이지 구조 분석
- [ ] Selenium 크롤러 구현
- [ ] 데이터 파싱 로직 구현
- [ ] 데이터베이스 스키마 구축
- [ ] 기본 데이터 저장 기능

### Phase 2: 스케줄링 및 자동화 (3일)
- [ ] APScheduler 통합
- [ ] 주기적 실행 설정
- [ ] 에러 처리 및 재시도 로직
- [ ] 로깅 시스템 구축

### Phase 3: 백엔드 API (1주)
- [ ] FastAPI 프로젝트 설정
- [ ] 데이터 조회 API 구현
- [ ] 분석 API 구현
- [ ] API 문서화 (Swagger)

### Phase 4: 프론트엔드 대시보드 (2주)
- [ ] React 프로젝트 설정
- [ ] 메인 대시보드 UI
- [ ] 상품 상세 페이지
- [ ] 브랜드 분석 페이지
- [ ] 차트 및 시각화

### Phase 5: 배포 및 최적화 (3일)
- [ ] Docker 컨테이너화
- [ ] Nginx 설정
- [ ] 프로덕션 배포
- [ ] 성능 최적화
- [ ] 모니터링 설정

**예상 총 소요 기간**: 약 4주

---

## 💰 예상 비용 (클라우드 배포 시)

### AWS 기준 (월 예상 비용)

| 항목 | 사양 | 월 비용 (USD) |
|------|------|--------------|
| EC2 (t3.medium) | 2 vCPU, 4GB RAM | $30 |
| RDS PostgreSQL (db.t3.micro) | 1 vCPU, 1GB RAM | $15 |
| ElastiCache Redis (선택) | cache.t3.micro | $12 |
| CloudWatch 로깅 | 기본 | $5 |
| 네트워크 전송 | 1GB | $0.09 |
| **총 예상 비용** | | **약 $62/월** |

### 대안: 저비용 옵션
- **Vercel** (프론트엔드): 무료
- **Railway/Render** (백엔드): $5~$20/월
- **Supabase** (데이터베이스): 무료 (500MB)
- **총 예상 비용**: **$5~$20/월**

---

## ✅ 최종 결론

### 모든 요구사항 구현 가능 ✅

1. **Top 200개 브랜드 & 제품 정보** → ✅ 가능
2. **브랜드별 제품 개수 집계** → ✅ 가능
3. **가격 변화 추적** → ✅ 가능
4. **정해진 시간마다 반복 실행** → ✅ 가능

### 핵심 성공 요소
1. ✅ Selenium을 통한 동적 페이지 크롤링
2. ✅ 시계열 데이터베이스 설계
3. ✅ 안정적인 스케줄링 시스템
4. ✅ 직관적인 대시보드

### 추가 가능한 기능
- 🔔 가격/순위 변동 알림 (이메일, 텔레그램)
- 📊 AI 기반 트렌드 예측
- 🏆 베스트 상품 추천 시스템
- 📈 엑셀 리포트 자동 생성
- 🔍 특정 브랜드/상품 모니터링

---

## 🚀 다음 단계

구현을 진행하시려면 다음 사항을 결정해주세요:

1. **실행 주기**: 몇 시간마다 크롤링하시겠습니까?
2. **데이터베이스**: PostgreSQL vs SQLite
3. **배포 환경**: 로컬 서버 vs 클라우드
4. **프론트엔드**: 필요 여부 및 선호하는 기술
5. **알림 기능**: 필요 여부 및 선호하는 방식

결정사항을 알려주시면 즉시 개발을 시작하겠습니다! 🎯
