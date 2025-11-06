import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = 'https://w-best-tracker.fly.dev';

function App() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalBrands: 0,
    totalCollections: 0
  });

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const healthRes = await fetch(`${API_BASE}/api/health`);
      const healthData = await healthRes.json();
      
      if (healthData.status === 'healthy') {
        setLastUpdate(healthData.latest_collection);
        setStats({
          totalProducts: healthData.total_products,
          totalBrands: healthData.total_brands,
          totalCollections: healthData.total_collections
        });
      }

      const productsRes = await fetch(`${API_BASE}/api/products/current`);
      
      if (!productsRes.ok) {
        throw new Error(`API 응답 실패: ${productsRes.status}`);
      }

      const productsData = await productsRes.json();

      const latestCollectionTime = productsData.reduce((latest, p) => {
        return p.collected_at > latest ? p.collected_at : latest;
      }, '');

      console.log('최신 수집 시간:', latestCollectionTime);

      const latestProducts = productsData.filter(
        p => p.collected_at === latestCollectionTime
      );

      console.log(`전체 제품: ${productsData.length}개 → 최신 데이터: ${latestProducts.length}개`);

      const hasieProducts = latestProducts.filter(p => p.brand_name === '하시에');

      console.log(`하시에 제품: ${hasieProducts.length}개`);

      hasieProducts.sort((a, b) => a.ranking - b.ranking);

      setProducts(hasieProducts);
      setLoading(false);
    } catch (err) {
      console.error('데이터 로딩 실패:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '업데이트 정보 없음';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'Asia/Seoul'
    }).format(date);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('ko-KR').format(price) + '원';
  };

  if (loading) {
    return (
      <div className="App">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>데이터 로딩 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="App">
        <div className="error-container">
          <h2>⚠️ 오류 발생</h2>
          <p>{error}</p>
          <button onClick={fetchData} className="retry-button">
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>🏆 W Concept Best Tracker</h1>
        <p className="subtitle">하시에(HASIE) 브랜드 순위 추적</p>
      </header>

      <div className="stats-container">
        <div className="stat-card">
          <div className="stat-value">{stats.totalProducts.toLocaleString()}</div>
          <div className="stat-label">총 제품 수</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.totalBrands.toLocaleString()}</div>
          <div className="stat-label">총 브랜드 수</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.totalCollections.toLocaleString()}</div>
          <div className="stat-label">수집 횟수</div>
        </div>
        <div className="stat-card highlight">
          <div className="stat-value">{products.length}</div>
          <div className="stat-label">하시에 제품</div>
        </div>
      </div>

      <div className="update-info">
        <span>📅 마지막 업데이트: {formatDate(lastUpdate)}</span>
        <button onClick={fetchData} className="refresh-button" title="새로고침">
          🔄
        </button>
      </div>

      <main className="products-container">
        <h2>우리 제품 (하시에)</h2>
        
        {products.length === 0 ? (
          <div className="no-products">
            <p>현재 순위권 내에 하시에 제품이 없습니다.</p>
          </div>
        ) : (
          <div className="products-grid">
            {products.map((product, index) => (
              <div key={product.product_id} className="product-card">
                <div className="product-rank">
                  <span className="rank-badge">#{product.ranking}</span>
                  {index === 0 && <span className="best-badge">👑 1위</span>}
                </div>
                <div className="product-image">
                  <img 
                    src={product.image_url} 
                    alt={product.product_name}
                    loading="lazy"
                    onError={(e) => {
                      e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23ddd" width="200" height="200"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" fill="%23999" dy=".3em"%3ENo Image%3C/text%3E%3C/svg%3E';
                    }}
                  />
                </div>
                <div className="product-info">
                  <h3 className="product-name">{product.product_name}</h3>
                  <div className="product-category">{product.category}</div>
                  <div className="product-price">
                    <span className="price">{formatPrice(product.price)}</span>
                    {product.discount_rate > 0 && (
                      <span className="discount">{product.discount_rate}% 할인</span>
                    )}
                  </div>
                  <a 
                    href={product.product_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="product-link"
                  >
                    제품 보기 →
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>
          <a 
            href="https://github.com/happypororo/W-Best-Tracker" 
            target="_blank" 
            rel="noopener noreferrer"
          >
            GitHub Repository
          </a>
          {' | '}
          <a 
            href={`${API_BASE}/api/docs`}
            target="_blank" 
            rel="noopener noreferrer"
          >
            API Documentation
          </a>
        </p>
        <p className="copyright">© 2025 W-Best-Tracker. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;
