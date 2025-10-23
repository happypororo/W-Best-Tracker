# W컨셉 베스트 상품 트래킹 시스템 - 사용 가이드

## 🎉 시스템 완성!

데이터베이스 + 자동화 스케줄러가 성공적으로 구축되었습니다!

---

## 📦 구성 요소

### 1. 크롤러 (wconcept_scraper_v2.py)
- W컨셉 베스트 200개 상품 수집
- 순위, 브랜드, 상품명, 가격, 할인율 추출
- JSON 파일로 저장

### 2. 데이터베이스 (database.py)
- SQLite 기반 시계열 데이터 저장
- 7개 테이블: 제품, 순위이력, 브랜드, 순위변동, 가격변동, 통계, 로그
- 자동 변동 감지 및 기록

### 3. 스케줄러 (scheduler.py)
- APScheduler 기반 자동 실행
- 매 N시간마다 또는 특정 시간에 실행
- 크롤링 → DB 저장 → 로깅 자동화

### 4. 분석 도구 (analytics.py)
- 현재 순위 조회
- 브랜드별 통계
- 상품 이력 추적
- 순위/가격 변동 분석
- JSON 내보내기

---

## 🚀 빠른 시작

### 1단계: 즉시 크롤링 실행
```bash
cd /home/user/webapp
python scheduler.py now
```

### 2단계: 데이터 확인
```bash
python analytics.py all
```

### 3단계: 자동화 시작
```bash
# 매 1시간마다 실행
python scheduler.py hourly

# 또는 매일 9, 12, 18, 21시에 실행
python scheduler.py cron
```

---

## 📖 상세 사용법

### 스케줄러 (scheduler.py)

#### 실행 모드

**즉시 한 번 실행**
```bash
python scheduler.py now
```

**매 시간마다 자동 실행**
```bash
python scheduler.py hourly          # 매 1시간
python scheduler.py hourly-2        # 매 2시간
```

**특정 시간에 실행**
```bash
python scheduler.py cron            # 매일 9, 12, 18, 21시
```

**테스트 모드 (매 1분)**
```bash
python scheduler.py test
```

**데이터베이스 통계만 보기**
```bash
python scheduler.py stats
```

#### 자동 실행 예제
```bash
# 터미널에서 실행 (Ctrl+C로 종료)
cd /home/user/webapp
python scheduler.py hourly

# 백그라운드 실행 (nohup)
nohup python scheduler.py hourly > scheduler.log 2>&1 &

# 프로세스 확인
ps aux | grep scheduler

# 종료
pkill -f scheduler.py
```

---

### 분석 도구 (analytics.py)

#### 명령어 목록

**1. 현재 순위**
```bash
python analytics.py rankings 20    # Top 20
python analytics.py rankings 50    # Top 50
python analytics.py rankings 200   # 전체
```

**2. 브랜드 통계**
```bash
python analytics.py brands         # 최근 24시간
python analytics.py brands 48      # 최근 48시간
python analytics.py brands 168     # 최근 1주일
```

**3. 상품 이력 조회**
```bash
# 먼저 상품 ID 확인
python analytics.py rankings 10

# 특정 상품 이력
python analytics.py history PROD_307602440
python analytics.py history PROD_307602440 14    # 최근 14일
```

**4. 순위 급변동**
```bash
python analytics.py movers-up      # 급상승 Top 10
python analytics.py movers-down    # 급하락 Top 10
```

**5. 가격 변동**
```bash
python analytics.py prices         # 최근 24시간
python analytics.py prices 48      # 최근 48시간
```

**6. 데이터베이스 통계**
```bash
python analytics.py stats
```

**7. JSON 내보내기**
```bash
python analytics.py export
python analytics.py export my_export.json
```

**8. 전체 리포트**
```bash
python analytics.py all
```

---

## 📊 데이터베이스 구조

### 테이블 설명

**1. products** (제품 기본 정보)
- product_id, product_name, brand_name
- image_url, product_url
- first_seen, last_seen

**2. ranking_history** (순위/가격 이력)
- product_id, ranking
- original_price, sale_price, discount_rate
- collected_at

**3. brands** (브랜드 정보)
- brand_name, total_products
- first_seen, last_updated

**4. brand_stats_history** (브랜드 통계 이력)
- brand_name, product_count
- avg_ranking, avg_price
- avg_discount_rate, collected_at

**5. ranking_changes** (순위 변동 로그)
- product_id, previous_ranking, current_ranking
- change_amount, change_type
- changed_at

**6. price_changes** (가격 변동 로그)
- product_id, previous_sale_price, current_sale_price
- price_change_amount, price_change_percentage
- changed_at

**7. scraping_logs** (크롤링 작업 로그)
- started_at, completed_at, status
- products_collected, error_message
- execution_time_seconds

---

## 💡 활용 시나리오

### 시나리오 1: 일일 모니터링

**오전 9시에 자동 크롤링**
```bash
# 스케줄러 시작 (한 번만 설정)
nohup python scheduler.py cron > logs/scheduler.log 2>&1 &

# 매일 오전에 리포트 확인
python analytics.py all > logs/daily_report_$(date +%Y%m%d).txt
```

### 시나리오 2: 특정 상품 추적

```bash
# 1. 관심 상품의 ID 확인
python analytics.py rankings 50 | grep "프론트로우"

# 2. 해당 상품 이력 조회
python analytics.py history PROD_307349815

# 3. 매일 확인 (crontab)
# 0 9 * * * cd /home/user/webapp && python analytics.py history PROD_307349815 >> product_track.log
```

### 시나리오 3: 브랜드 분석

```bash
# 주간 브랜드 보고서
python analytics.py brands 168 > reports/weekly_brands.txt

# 월간 데이터 내보내기
python analytics.py export reports/monthly_$(date +%Y%m).json
```

### 시나리오 4: 가격 변동 알림

```python
# price_alert.py 작성
from database import Database

db = Database()
changes = db.get_price_changes(hours=1)

# 가격 인하 상품 확인
if changes['price_decreased']:
    for item in changes['price_decreased'][:5]:
        discount_pct = abs(item['price_change_percentage'])
        if discount_pct > 10:  # 10% 이상 인하
            print(f"🔔 알림: {item['brand_name']} {item['product_name']}")
            print(f"   {discount_pct:.1f}% 가격 인하!")
            # 이메일/텔레그램 알림 보내기
```

---

## 🔧 고급 설정

### Cron Job 설정 (Linux)

```bash
# crontab 편집
crontab -e

# 매일 9, 12, 18, 21시에 크롤링
0 9,12,18,21 * * * cd /home/user/webapp && python scheduler.py now >> /home/user/webapp/logs/cron.log 2>&1

# 매일 오전 8시에 일일 리포트 생성
0 8 * * * cd /home/user/webapp && python analytics.py all > /home/user/webapp/reports/daily_$(date +\%Y\%m\%d).txt
```

### systemd 서비스 (Linux)

```bash
# /etc/systemd/system/wconcept-scheduler.service
[Unit]
Description=W컨셉 자동 크롤링 스케줄러
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/user/webapp
ExecStart=/usr/bin/python3 /home/user/webapp/scheduler.py hourly
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 등록 및 시작
sudo systemctl daemon-reload
sudo systemctl enable wconcept-scheduler
sudo systemctl start wconcept-scheduler

# 상태 확인
sudo systemctl status wconcept-scheduler

# 로그 확인
sudo journalctl -u wconcept-scheduler -f
```

---

## 📈 데이터 활용 예제

### Python 스크립트에서 사용

```python
from database import Database

db = Database()

# 현재 Top 10 조회
products = db.get_latest_rankings(limit=10)
for p in products:
    print(f"{p['ranking']}. {p['brand_name']} - {p['product_name']}")

# 브랜드 통계
stats = db.get_brand_statistics(hours=24)
for brand in stats[:5]:
    print(f"{brand['brand_name']}: {brand['avg_product_count']:.0f}개")

# 특정 상품 이력
history = db.get_product_history('PROD_307602440', days=7)
print(f"데이터 포인트: {len(history)}개")
```

### SQL 쿼리 직접 실행

```bash
# SQLite CLI
sqlite3 wconcept_tracking.db

# 쿼리 예제
SELECT brand_name, COUNT(*) as count 
FROM ranking_history rh
JOIN products p ON rh.product_id = p.product_id
WHERE rh.collected_at = (SELECT MAX(collected_at) FROM ranking_history)
GROUP BY brand_name
ORDER BY count DESC
LIMIT 10;
```

---

## 🐛 문제 해결

### 크롤링 실패

**증상**: 상품이 수집되지 않음

**해결**:
```bash
# 1. 네트워크 연결 확인
ping display.wconcept.co.kr

# 2. 브라우저 재설치
playwright install chromium --force

# 3. 수동 실행으로 에러 확인
python wconcept_scraper_v2.py
```

### 데이터베이스 오류

**증상**: Database is locked

**해결**:
```bash
# 1. 실행 중인 프로세스 확인
ps aux | grep python

# 2. 데이터베이스 파일 권한 확인
ls -l wconcept_tracking.db

# 3. 백업 후 재생성
cp wconcept_tracking.db wconcept_tracking.db.bak
rm wconcept_tracking.db
python database.py
```

### 스케줄러 중지

**증상**: 스케줄러가 종료되지 않음

**해결**:
```bash
# 프로세스 강제 종료
pkill -9 -f scheduler.py

# 또는 프로세스 ID로 종료
ps aux | grep scheduler
kill -9 <PID>
```

---

## 📦 백업 및 복원

### 데이터베이스 백업

```bash
# 백업 생성
cp wconcept_tracking.db backups/wconcept_$(date +%Y%m%d).db

# 압축 백업
tar -czf backups/wconcept_$(date +%Y%m%d).tar.gz wconcept_tracking.db

# 자동 백업 (cron)
# 매일 새벽 2시
0 2 * * * cd /home/user/webapp && cp wconcept_tracking.db backups/wconcept_$(date +\%Y\%m\%d).db
```

### 복원

```bash
# 백업에서 복원
cp backups/wconcept_20251023.db wconcept_tracking.db

# 압축 파일에서 복원
tar -xzf backups/wconcept_20251023.tar.gz
```

---

## 📊 성능 최적화

### 데이터베이스 최적화

```bash
# SQLite 진공 청소 (공간 회수)
sqlite3 wconcept_tracking.db "VACUUM;"

# 분석 및 최적화
sqlite3 wconcept_tracking.db "ANALYZE;"
```

### 오래된 데이터 정리

```python
# cleanup.py
from database import Database
from datetime import datetime, timedelta

db = Database()

# 90일 이전 데이터 삭제
cutoff_date = datetime.now() - timedelta(days=90)

with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM ranking_history 
        WHERE collected_at < ?
    """, (cutoff_date,))
    print(f"{cursor.rowcount}개 레코드 삭제됨")
```

---

## 🎯 다음 단계

1. **API 서버 구축** → FastAPI로 데이터 제공
2. **웹 대시보드** → React로 시각화
3. **알림 시스템** → 이메일/텔레그램 통합
4. **머신러닝** → 트렌드 예측 모델

---

## 📞 도움말

### 명령어 도움말
```bash
python scheduler.py              # 스케줄러 사용법
python analytics.py              # 분석 도구 사용법
```

### 파일 위치
```
/home/user/webapp/
├── wconcept_scraper_v2.py      # 크롤러
├── database.py                  # 데이터베이스
├── scheduler.py                 # 스케줄러
├── analytics.py                 # 분석 도구
├── wconcept_tracking.db         # 데이터베이스 파일
├── wconcept_data_*.json         # 수집 데이터
└── USER_GUIDE.md               # 이 파일
```

---

## ✅ 시스템 상태 확인

```bash
# 전체 상태 확인 스크립트
cd /home/user/webapp

echo "=== 데이터베이스 상태 ==="
python analytics.py stats

echo -e "\n=== 최신 데이터 ==="
python analytics.py rankings 5

echo -e "\n=== 브랜드 Top 5 ==="
python analytics.py brands | head -15

echo -e "\n=== 파일 확인 ==="
ls -lh wconcept_tracking.db
ls -lh wconcept_data_*.json | tail -3
```

---

## 🎉 완료!

모든 기능이 정상 작동합니다!

**다음 명령으로 시스템을 시작하세요**:
```bash
cd /home/user/webapp
python scheduler.py hourly
```

**그리고 다른 터미널에서 데이터를 확인하세요**:
```bash
cd /home/user/webapp
python analytics.py all
```

즐거운 데이터 분석 되세요! 🚀
