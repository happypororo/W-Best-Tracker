# W컨셉 베스트 상품 트래킹 시스템 - 구현 가이드

## 🚨 중요 발견 사항

### 봇 차단 시스템
W컨셉 사이트는 매우 강력한 봇 차단 메커니즘을 사용하고 있습니다:

1. **기본 HTTP 요청**: "정상적인 조회형식이 아닙니다" 메시지 반환
2. **Selenium 접근**: 페이지 로딩 후 `about:blank`로 리다이렉트
3. **Playwright 접근**: 동일하게 차단됨

### 차단 원인 분석
- ✅ User-Agent 검증
- ✅ Headless 브라우저 감지
- ✅ WebDriver 감지
- ✅ 자동화 도구 감지 (navigator.webdriver)
- ⚠️ IP 기반 필터링 가능성
- ⚠️ CAPTCHA 또는 Challenge 시스템

---

## 💡 해결 방안

### 방안 1: 고급 봇 회피 기술 (권장하지 않음)

```python
# undetected-chromedriver 사용
import undetected_chromedriver as uc

driver = uc.Chrome()
driver.get('https://www.wconcept.co.kr/Product/Best')
```

**문제점**:
- 법적/윤리적 문제 발생 가능
- W컨셉의 이용약관 위반 가능성
- 지속적인 업데이트 필요
- 서비스 차단 위험

### 방안 2: 공식 API 사용 (최선)

W컨셉에 공식 API 제공 여부 문의:
- 파트너십 프로그램
- 개발자 API
- 데이터 제공 서비스

**장점**:
- 합법적이고 안정적
- 고품질 데이터
- 장기적으로 지속 가능

### 방안 3: 수동 데이터 수집

브라우저 확장 프로그램 개발:
- 사용자가 직접 브라우저로 접속
- 확장 프로그램이 데이터 수집
- 자동화 규칙 위반하지 않음

### 방안 4: 대안 데이터 소스

다른 패션 이커머스 플랫폼:
- 무신사 (Musinsa)
- 에이블리 (Ably)
- 지그재그 (Zigzag)
- 29CM

---

## 📋 권장 구현 방식

### 옵션 A: 합법적 접근 (강력 추천)

1. **W컨셉에 공식 문의**
   ```
   제목: 데이터 분석을 위한 API 사용 문의
   
   안녕하세요,
   
   저는 패션 시장 트렌드 분석 프로젝트를 진행 중입니다.
   W컨셉의 베스트 상품 순위 데이터를 활용하고자 하는데,
   공식 API나 데이터 제공 서비스가 있는지 문의드립니다.
   
   목적: 학술/개인 연구용 데이터 분석
   필요 데이터: 베스트 상품 순위, 가격, 브랜드 정보
   
   감사합니다.
   ```

2. **브라우저 확장 프로그램 개발**
   - Chrome Extension으로 구현
   - 사용자가 직접 페이지 방문
   - 백그라운드에서 데이터 수집
   - 로컬 데이터베이스에 저장

3. **RSS/공개 데이터 활용**
   - W컨셉 공식 블로그/뉴스레터
   - 소셜 미디어 데이터
   - 공개된 순위 정보

### 옵션 B: 브라우저 확장 프로그램

#### Chrome Extension 구조

```
wconcept-tracker/
├── manifest.json
├── background.js
├── content.js
├── popup/
│   ├── popup.html
│   ├── popup.js
│   └── popup.css
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

#### manifest.json
```json
{
  "manifest_version": 3,
  "name": "W컨셉 순위 트래커",
  "version": "1.0.0",
  "description": "W컨셉 베스트 상품 순위 추적",
  "permissions": [
    "storage",
    "activeTab"
  ],
  "host_permissions": [
    "https://www.wconcept.co.kr/*"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [{
    "matches": ["https://www.wconcept.co.kr/Product/Best*"],
    "js": ["content.js"]
  }],
  "action": {
    "default_popup": "popup/popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  }
}
```

#### content.js (실제 데이터 수집)
```javascript
// 페이지에서 상품 정보 추출
function extractProducts() {
  const products = [];
  
  // 페이지의 실제 셀렉터 사용 (개발자 도구로 확인 필요)
  const productElements = document.querySelectorAll('.product-item'); // 예시
  
  productElements.forEach((elem, index) => {
    const product = {
      rank: index + 1,
      name: elem.querySelector('.product-name')?.textContent,
      brand: elem.querySelector('.brand-name')?.textContent,
      price: elem.querySelector('.price')?.textContent,
      image: elem.querySelector('img')?.src,
      url: elem.querySelector('a')?.href,
      timestamp: new Date().toISOString()
    };
    
    products.push(product);
  });
  
  return products;
}

// 데이터를 백그라운드 스크립트로 전송
chrome.runtime.sendMessage({
  type: 'PRODUCTS_EXTRACTED',
  data: extractProducts()
});
```

#### background.js (데이터 저장)
```javascript
// 데이터 수신 및 저장
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'PRODUCTS_EXTRACTED') {
    // Chrome Storage에 저장
    chrome.storage.local.get(['history'], (result) => {
      const history = result.history || [];
      history.push({
        timestamp: new Date().toISOString(),
        products: message.data
      });
      
      chrome.storage.local.set({ history });
    });
  }
});
```

---

## 🎯 실용적인 대안 시스템

### 시스템 1: 수동 + 자동 하이브리드

```python
# 사용자가 수동으로 HTML 파일 저장
# 프로그램이 저장된 HTML 파일 분석

import os
from datetime import datetime
from bs4 import BeautifulSoup
import sqlite3

def parse_saved_html(html_file):
    """저장된 HTML 파일 파싱"""
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    products = []
    # 파싱 로직...
    
    return products

def save_to_database(products):
    """데이터베이스에 저장"""
    conn = sqlite3.connect('wconcept_tracking.db')
    # 저장 로직...
    conn.close()

# 사용법
# 1. 사용자가 브라우저에서 페이지를 열고 "다른 이름으로 저장"
# 2. 저장된 HTML 파일을 지정된 폴더에 복사
# 3. 프로그램이 주기적으로 폴더를 스캔하여 새 파일 처리
```

### 시스템 2: 모바일 앱 (React Native)

사용자가 앱에서 직접 W컨셉 페이지를 보면서 데이터 수집:
- WebView로 실제 페이지 표시
- 사용자가 직접 스크롤하며 탐색
- 백그라운드에서 데이터 추출 및 저장

---

## 📊 데이터 수집 없이 구현 가능한 기능

### Mock 데이터로 시스템 구축

실제 크롤링 없이 시스템의 나머지 부분을 먼저 구축:

1. **Mock 데이터 생성기**
```python
import random
from datetime import datetime, timedelta

def generate_mock_data(num_products=200):
    """가상의 상품 데이터 생성"""
    brands = ['GUCCI', 'PRADA', 'BALENCIAGA', 'MONCLER', 'BURBERRY']
    products = []
    
    for i in range(num_products):
        products.append({
            'rank': i + 1,
            'product_id': f'PROD_{i+1:04d}',
            'name': f'Sample Product {i+1}',
            'brand': random.choice(brands),
            'price': random.randint(50000, 500000),
            'timestamp': datetime.now()
        })
    
    return products
```

2. **전체 시스템 구축**
   - ✅ 데이터베이스 스키마
   - ✅ FastAPI 백엔드
   - ✅ React 프론트엔드
   - ✅ 차트 및 대시보드
   - ✅ 스케줄러

3. **나중에 실제 데이터 소스 연결**
   - Mock 데이터 생성기를 실제 크롤러로 교체
   - 또는 브라우저 확장 프로그램 연결
   - 또는 공식 API 연결

---

## 💼 비즈니스 관점의 제안

### 합법적으로 목표 달성하기

1. **W컨셉과 파트너십**
   - 데이터 분석 서비스 제안
   - 마케팅 인사이트 제공
   - 상호 이익이 되는 협력 관계

2. **공개 데이터만 사용**
   - W컨셉 공식 SNS
   - 보도자료 및 공개 리포트
   - 검색 트렌드 데이터

3. **유사 서비스 개발**
   - 크롤링 가능한 다른 플랫폼 활용
   - 자체 큐레이션 시스템 구축
   - 사용자 생성 데이터 기반 순위

---

## 🚀 다음 단계 선택지

### A. 합법적 접근 (권장)
1. W컨셉에 공식 문의
2. 브라우저 확장 프로그램 개발
3. Mock 데이터로 시스템 먼저 구축

### B. 대안 플랫폼
1. 무신사, 에이블리 등 다른 플랫폼 시도
2. 크롤링 가능 여부 확인
3. 동일한 시스템 구축

### C. 하이브리드 방식
1. 수동으로 HTML 저장
2. 프로그램이 자동 분석
3. 데이터 축적 및 시각화

---

## 📝 결론

### ✅ 기술적으로 구현 가능한 것들

1. ✅ Top 200개 제품 정보 수집 - **가능** (적절한 방법 사용 시)
2. ✅ 브랜드별 제품 개수 - **가능**
3. ✅ 가격 변화 추적 - **가능**
4. ✅ 주기적 반복 실행 - **가능**

### ⚠️ 주의사항

- **법적 리스크**: 크롤링은 이용약관 위반 가능
- **윤리적 문제**: 봇 차단을 우회하는 것은 비윤리적
- **지속 가능성**: 차단 시스템은 계속 진화함

### 💡 권장 사항

1. **1순위**: W컨셉에 공식 API 사용 문의
2. **2순위**: 브라우저 확장 프로그램 개발 (사용자 주도)
3. **3순위**: Mock 데이터로 시스템 구축 후 합법적 소스 연결
4. **4순위**: 대안 플랫폼 (무신사, 에이블리 등) 활용

---

## 🤝 제가 도와드릴 수 있는 것

현재 상황에서 제가 바로 구현해드릴 수 있는 것:

1. ✅ **Mock 데이터 기반 전체 시스템**
   - 데이터베이스 설계
   - FastAPI 백엔드
   - React 대시보드
   - 순위 추적 로직
   - 가격 변동 분석
   - 차트 및 시각화

2. ✅ **브라우저 확장 프로그램**
   - Chrome Extension 개발
   - 데이터 수집 로직
   - 로컬 저장소 관리

3. ✅ **수동 데이터 처리 시스템**
   - HTML 파일 파싱
   - 데이터 정규화
   - 데이터베이스 저장

어떤 방향으로 진행하시겠습니까?
