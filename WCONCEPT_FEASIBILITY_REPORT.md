# W컨셉 베스트 상품 랭킹 트래커 개발 가능성 분석 보고서

## 📋 요구사항 분석

### 1. Top 200개 브랜드 & 제품 정보 수집
**결론: ✅ 구현 가능**

- **방법**: Selenium + BeautifulSoup4 조합
- **이유**: W컨셉 사이트는 봇 차단 기능이 있어 일반 HTTP 요청으로는 접근 불가
- **구현 방식**:
  - Selenium으로 실제 브라우저 시뮬레이션
  - 동적으로 로드되는 컨텐츠 대기 및 수집
  - 페이지네이션 또는 무한 스크롤 처리

**예상 수집 가능 데이터**:
```python
{
    "rank": 1,
    "product_id": "12345",
    "product_name": "상품명",
    "brand_name": "브랜드명",
    "price": 59000,
    "discount_price": 49000,
    "discount_rate": 17,
    "image_url": "https://...",
    "product_url": "https://...",
    "timestamp": "2025-10-23 10:00:00"
}
```

### 2. 브랜드별 제품 개수 집계
**결론: ✅ 구현 가능**

- **방법**: SQL GROUP BY 쿼리 또는 Python 데이터 처리
- **전제조건**: 1번이 성공적으로 구현되어야 함
- **구현 예시**:
```sql
SELECT 
    brand_name, 
    COUNT(*) as product_count,
    AVG(rank) as avg_rank
FROM products
WHERE timestamp = (SELECT MAX(timestamp) FROM products)
GROUP BY brand_name
ORDER BY product_count DESC;
```

### 3. 가격 변화 추적
**결론: ✅ 구현 가능**

- **방법**: 시계열 데이터베이스 설계
- **저장 방식**: 각 수집 시점마다 전체 데이터 스냅샷 저장
- **분석 기능**:
  - 가격 인상/인하 추적
  - 할인율 변화 모니터링
  - 가격 히스토리 차트 생성

**데이터베이스 스키마 예시**:
```sql
CREATE TABLE product_snapshots (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(50),
    rank INTEGER,
    product_name TEXT,
    brand_name VARCHAR(100),
    price INTEGER,
    discount_price INTEGER,
    discount_rate DECIMAL(5,2),
    collected_at TIMESTAMP,
    INDEX idx_product_time (product_id, collected_at),
    INDEX idx_brand (brand_name),
    INDEX idx_rank (rank)
);
```

### 4. 정해진 시간마다 반복 실행
**결론: ✅ 구현 가능**

- **방법 1**: APScheduler (Python 스케줄러)
- **방법 2**: Cron Job (Linux)
- **방법 3**: Celery + Redis (대규모 프로젝트용)

**APScheduler 구현 예시**:
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=scrape_wconcept_best,
    trigger="interval",
    hours=1,  # 1시간마다
    id="wconcept_scraper",
    replace_existing=True
)
scheduler.start()
```

---

## 🚨 주요 이슈 및 해결 방안

### 이슈 1: 봇 차단 (Bot Detection)
**현상**: 일반 HTTP 요청 시 "정상적인 조회형식이 아닙니다" 메시지 반환

**해결 방안**:
1. **Selenium 사용** (권장)
   - 실제 브라우저 동작 시뮬레이션
   - User-Agent, Referer 등 헤더 설정
   - 랜덤 딜레이 추가 (봇 감지 회피)

2. **Headless Browser 설정**:
```python
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
```

3. **요청 간격 조절**:
   - 최소 3-5초 딜레이
   - 랜덤 스크롤 동작 추가
   - 세션 유지 및 쿠키 관리

### 이슈 2: 동적 컨텐츠 로딩
**현상**: JavaScript로 상품 목록이 동적 로드

**해결 방안**:
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 특정 요소가 로드될 때까지 대기
wait = WebDriverWait(driver, 10)
element = wait.until(
    EC.presence_of_element_located((By.CLASS_NAME, "product-item"))
)
```

### 이슈 3: 무한 스크롤 처리
**해결 방안**:
```python
def scroll_to_load_all(driver, target_count=200):
    last_height = driver.execute_script("return document.body.scrollHeight")
    products_loaded = 0
    
    while products_loaded < target_count:
        # 스크롤 다운
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # 새로운 높이 확인
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # 상품 개수 확인
        products = driver.find_elements(By.CLASS_NAME, "product-item")
        products_loaded = len(products)
        
        # 더 이상 로드되지 않으면 종료
        if new_height == last_height:
            break
            
        last_height = new_height
```

---

## 🏗️ 권장 시스템 아키텍처

### 기술 스택

#### 백엔드
- **언어**: Python 3.10+
- **프레임워크**: FastAPI
- **크롤링**: Selenium + BeautifulSoup4
- **데이터베이스**: PostgreSQL (또는 SQLite for development)
- **스케줄링**: APScheduler
- **캐싱**: Redis (optional)

#### 프론트엔드
- **프레임워크**: React or Vue.js
- **차트 라이브러리**: Chart.js, Recharts, or Plotly
- **UI 라이브러리**: TailwindCSS, Material-UI

#### 인프라
- **컨테이너**: Docker + Docker Compose
- **프록시**: Nginx
- **모니터링**: Prometheus + Grafana (optional)

### 시스템 구조도

```
┌─────────────────┐
│   Web Browser   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  React Frontend │
│   (Dashboard)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│   FastAPI       │◄────►│  PostgreSQL  │
│   (REST API)    │      │  (Database)  │
└────────┬────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  APScheduler    │      │   Selenium   │
│  (Scheduler)    │─────►│   (Scraper)  │
└─────────────────┘      └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │  W Concept   │
                         │   Website    │
                         └──────────────┘
```

---

## 📊 데이터베이스 스키마 설계

### 테이블 1: products
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    product_name TEXT NOT NULL,
    brand_name VARCHAR(100) NOT NULL,
    product_url TEXT,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id)
);
```

### 테이블 2: rankings
```sql
CREATE TABLE rankings (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    rank INTEGER NOT NULL,
    price INTEGER,
    discount_price INTEGER,
    discount_rate DECIMAL(5,2),
    collected_at TIMESTAMP NOT NULL,
    INDEX idx_product_time (product_id, collected_at),
    INDEX idx_rank_time (rank, collected_at),
    INDEX idx_collected_at (collected_at),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

### 테이블 3: brands
```sql
CREATE TABLE brands (
    id SERIAL PRIMARY KEY,
    brand_name VARCHAR(100) UNIQUE NOT NULL,
    total_products INTEGER DEFAULT 0,
    avg_rank DECIMAL(5,2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 테이블 4: price_changes
```sql
CREATE TABLE price_changes (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    old_price INTEGER,
    new_price INTEGER,
    change_percentage DECIMAL(5,2),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

---

## 🔧 주요 기능 구현 가이드

### 1. 크롤러 구현

```python
# scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random

class WConceptScraper:
    def __init__(self):
        self.setup_driver()
        
    def setup_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.driver = webdriver.Chrome(options=options)
        
    def scrape_best_products(self, limit=200):
        url = "https://www.wconcept.co.kr/Product/Best"
        self.driver.get(url)
        
        # 페이지 로드 대기
        time.sleep(random.uniform(2, 4))
        
        # 스크롤하여 모든 상품 로드
        products = self._load_all_products(limit)
        
        # 데이터 파싱
        return self._parse_products(products)
    
    def _load_all_products(self, target_count):
        loaded = 0
        while loaded < target_count:
            # 스크롤 다운
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 2))
            
            # 상품 개수 확인
            products = self.driver.find_elements(By.CSS_SELECTOR, ".product-item")  # 실제 셀렉터로 교체 필요
            loaded = len(products)
            
            if loaded >= target_count:
                break
                
        return products[:target_count]
    
    def _parse_products(self, products):
        results = []
        for idx, product in enumerate(products, 1):
            try:
                data = {
                    'rank': idx,
                    'product_name': product.find_element(By.CSS_SELECTOR, '.product-name').text,
                    'brand_name': product.find_element(By.CSS_SELECTOR, '.brand-name').text,
                    'price': self._extract_price(product),
                    'product_url': product.find_element(By.TAG_NAME, 'a').get_attribute('href'),
                    'image_url': product.find_element(By.TAG_NAME, 'img').get_attribute('src'),
                }
                results.append(data)
            except Exception as e:
                print(f"Error parsing product {idx}: {e}")
                continue
        
        return results
    
    def _extract_price(self, product):
        # 가격 추출 로직 (실제 구조에 맞게 수정 필요)
        try:
            price_text = product.find_element(By.CSS_SELECTOR, '.price').text
            return int(price_text.replace(',', '').replace('원', ''))
        except:
            return None
    
    def close(self):
        self.driver.quit()
```

### 2. 데이터베이스 매니저

```python
# database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(String(50), unique=True, nullable=False)
    product_name = Column(Text, nullable=False)
    brand_name = Column(String(100), nullable=False)
    product_url = Column(Text)
    image_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Ranking(Base):
    __tablename__ = 'rankings'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(String(50), nullable=False)
    rank = Column(Integer, nullable=False)
    price = Column(Integer)
    discount_price = Column(Integer)
    discount_rate = Column(Numeric(5, 2))
    collected_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self, db_url='sqlite:///wconcept.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def save_products(self, products_data):
        for data in products_data:
            # Product 저장/업데이트
            product = self.session.query(Product).filter_by(
                product_id=data['product_id']
            ).first()
            
            if not product:
                product = Product(**data)
                self.session.add(product)
            
            # Ranking 저장
            ranking = Ranking(
                product_id=data['product_id'],
                rank=data['rank'],
                price=data['price'],
                discount_price=data.get('discount_price'),
                discount_rate=data.get('discount_rate'),
                collected_at=datetime.utcnow()
            )
            self.session.add(ranking)
        
        self.session.commit()
```

### 3. 스케줄러 구현

```python
# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from scraper import WConceptScraper
from database import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RankingScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scraper = WConceptScraper()
        self.db = DatabaseManager()
    
    def scrape_and_save(self):
        logger.info("Starting scraping job...")
        try:
            products = self.scraper.scrape_best_products(limit=200)
            logger.info(f"Scraped {len(products)} products")
            
            self.db.save_products(products)
            logger.info("Data saved to database")
            
        except Exception as e:
            logger.error(f"Scraping job failed: {e}")
    
    def start(self, interval_hours=1):
        # 매 시간마다 실행
        self.scheduler.add_job(
            func=self.scrape_and_save,
            trigger="interval",
            hours=interval_hours,
            id="wconcept_scraper",
            replace_existing=True
        )
        
        # 즉시 한 번 실행
        self.scrape_and_save()
        
        # 스케줄러 시작
        self.scheduler.start()
        logger.info(f"Scheduler started (interval: {interval_hours} hours)")
```

### 4. FastAPI 백엔드

```python
# main.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from database import DatabaseManager, Ranking, Product
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI(title="W Concept Ranking Tracker")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DatabaseManager()

@app.get("/api/rankings/latest")
async def get_latest_rankings(limit: int = Query(200, le=200)):
    """최신 랭킹 조회"""
    latest_time = db.session.query(func.max(Ranking.collected_at)).scalar()
    
    rankings = db.session.query(Ranking, Product)\
        .join(Product, Ranking.product_id == Product.product_id)\
        .filter(Ranking.collected_at == latest_time)\
        .order_by(Ranking.rank)\
        .limit(limit)\
        .all()
    
    return [
        {
            "rank": r.Ranking.rank,
            "product_name": r.Product.product_name,
            "brand_name": r.Product.brand_name,
            "price": r.Ranking.price,
            "discount_price": r.Ranking.discount_price,
            "product_url": r.Product.product_url,
            "image_url": r.Product.image_url,
        }
        for r in rankings
    ]

@app.get("/api/brands/stats")
async def get_brand_stats():
    """브랜드별 통계"""
    latest_time = db.session.query(func.max(Ranking.collected_at)).scalar()
    
    stats = db.session.query(
        Product.brand_name,
        func.count(Ranking.id).label('product_count'),
        func.avg(Ranking.rank).label('avg_rank'),
        func.min(Ranking.rank).label('best_rank')
    ).join(Product, Ranking.product_id == Product.product_id)\
     .filter(Ranking.collected_at == latest_time)\
     .group_by(Product.brand_name)\
     .order_by(desc('product_count'))\
     .all()
    
    return [
        {
            "brand_name": s.brand_name,
            "product_count": s.product_count,
            "avg_rank": round(float(s.avg_rank), 2),
            "best_rank": s.best_rank
        }
        for s in stats
    ]

@app.get("/api/products/{product_id}/history")
async def get_product_history(
    product_id: str,
    days: int = Query(7, le=30)
):
    """특정 상품의 순위/가격 변화 이력"""
    since = datetime.utcnow() - timedelta(days=days)
    
    history = db.session.query(Ranking)\
        .filter(Ranking.product_id == product_id)\
        .filter(Ranking.collected_at >= since)\
        .order_by(Ranking.collected_at)\
        .all()
    
    return [
        {
            "rank": h.rank,
            "price": h.price,
            "discount_price": h.discount_price,
            "collected_at": h.collected_at.isoformat()
        }
        for h in history
    ]

@app.get("/api/price-changes")
async def get_price_changes(hours: int = Query(24, le=168)):
    """최근 가격 변동 내역"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # 가격 변동 감지 로직
    # (구현 복잡도를 위해 간단한 예시만 제공)
    
    return {"message": "Price change detection logic to be implemented"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 📈 대시보드 기능 설계

### 핵심 화면 구성

#### 1. 메인 대시보드
- **현재 Top 200 랭킹 테이블**
  - 순위, 상품명, 브랜드, 가격, 할인율
  - 정렬, 필터링, 검색 기능
  
- **브랜드별 통계 차트**
  - 브랜드별 상품 개수 (Bar Chart)
  - 브랜드별 평균 순위 (Bubble Chart)

#### 2. 상품 상세 페이지
- **순위 변화 그래프**
  - 시간에 따른 순위 변동 (Line Chart)
  
- **가격 변화 그래프**
  - 정가, 할인가 추이 (Line Chart)
  
- **알림 설정**
  - 순위 변동 알림
  - 가격 변동 알림

#### 3. 브랜드 분석 페이지
- **브랜드별 상품 목록**
- **브랜드 순위 추이**
- **시장 점유율 분석**

#### 4. 가격 모니터링 페이지
- **최근 가격 인상 상품**
- **최근 가격 인하 상품**
- **할인율 변화 추적**

---

## ⏱️ 예상 개발 일정

### Phase 1: 기본 크롤러 개발 (1주)
- [ ] Selenium 설정 및 W컨셉 접근 테스트
- [ ] 상품 데이터 파싱 로직 구현
- [ ] 200개 상품 수집 검증

### Phase 2: 데이터베이스 구축 (3일)
- [ ] 스키마 설계 및 생성
- [ ] ORM 모델 구현
- [ ] 데이터 저장 로직 구현

### Phase 3: 스케줄러 구현 (2일)
- [ ] APScheduler 설정
- [ ] 주기적 실행 테스트
- [ ] 에러 핸들링 및 로깅

### Phase 4: REST API 개발 (1주)
- [ ] FastAPI 프로젝트 설정
- [ ] 주요 엔드포인트 구현
- [ ] API 문서화 (Swagger)

### Phase 5: 프론트엔드 개발 (2주)
- [ ] React 프로젝트 설정
- [ ] 랭킹 테이블 컴포넌트
- [ ] 차트 및 그래프 구현
- [ ] 반응형 디자인

### Phase 6: 테스트 및 배포 (3일)
- [ ] 통합 테스트
- [ ] Docker 컨테이너화
- [ ] 배포 및 모니터링 설정

**총 예상 기간**: 약 4-5주

---

## 💰 예상 비용 (월간)

### 서버 비용
- **VPS 호스팅** (DigitalOcean/AWS): $10-20/월
- **데이터베이스** (Managed PostgreSQL): $15-30/월
- **총 예상**: $25-50/월

### 개발 비용
- **프리랜서 개발자**: $2,000-4,000 (일회성)
- **유지보수**: $500-1,000/월

---

## ⚠️ 법적/윤리적 고려사항

### 1. 이용약관 확인
- W컨셉 사이트의 이용약관 및 robots.txt 확인 필요
- 크롤링 금지 조항이 있을 수 있음

### 2. 크롤링 에티켓
- 서버에 부하를 주지 않도록 적절한 딜레이 설정
- User-Agent 명시
- 과도한 요청 자제

### 3. 데이터 사용 범위
- 수집한 데이터의 상업적 사용 제한 가능성
- 개인적 분석 용도로 제한 권장

### 4. 대안
- W컨셉 공식 API 제공 여부 확인
- 파트너십 또는 제휴 문의

---

## 🎯 결론 및 권장사항

### ✅ 기술적 구현 가능성: 100%

모든 요구사항은 **기술적으로 구현 가능**합니다:

1. ✅ Top 200개 수집 - **가능**
2. ✅ 브랜드별 통계 - **가능**
3. ✅ 가격 변화 추적 - **가능**
4. ✅ 자동 반복 실행 - **가능**

### 📋 다음 단계

1. **법적 검토**
   - W컨셉 이용약관 확인
   - 공식 API 제공 여부 문의

2. **프로토타입 개발**
   - 실제 페이지 구조 분석
   - 정확한 CSS 셀렉터 확인
   - 샘플 데이터 수집 테스트

3. **기술 스택 확정**
   - 개발 환경 설정
   - 필요 라이브러리 설치

4. **본격 개발 시작**
   - Phase 1부터 순차적 진행

### 🚀 시작하기 위한 명령어

```bash
# 프로젝트 초기화
mkdir wconcept-tracker
cd wconcept-tracker

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필수 패키지 설치
pip install selenium beautifulsoup4 sqlalchemy fastapi uvicorn apscheduler

# 프로젝트 구조 생성
mkdir -p src/{scraper,database,api,scheduler} tests data
touch src/__init__.py src/scraper/__init__.py src/database/__init__.py

# 개발 시작!
```

---

**준비되셨나요? 본격적으로 개발을 시작하시겠습니까?** 🚀
