import { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

const API_BASE = 'https://8000-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai';

function App() {
  const [products, setProducts] = useState([]);
  const [allProducts, setAllProducts] = useState([]);
  const [brands, setBrands] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [hashieRank, setHashieRank] = useState(null);
  const [hashieProducts, setHashieProducts] = useState([]);
  const [hashieInTop10, setHashieInTop10] = useState(0);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 1800000); // 30분마다 갱신 (30분 = 1800000ms)
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [productsRes, allProductsRes, brandsRes, statsRes] = await Promise.all([
        axios.get(`${API_BASE}/api/products/current?limit=10`),
        axios.get(`${API_BASE}/api/products/current?limit=200`),
        axios.get(`${API_BASE}/api/brands/stats?limit=10`),
        axios.get(`${API_BASE}/api/health`)
      ]);
      setProducts(productsRes.data);
      setAllProducts(allProductsRes.data);
      setBrands(brandsRes.data);
      setStats(statsRes.data);
      
      // 하시에 제품 모두 찾기
      const allHashieProducts = allProductsRes.data.filter(p => p.brand_name === '하시에');
      setHashieProducts(allHashieProducts);
      
      // 가장 높은 순위 찾기
      if (allHashieProducts.length > 0) {
        const topHashieRank = Math.min(...allHashieProducts.map(p => p.ranking));
        setHashieRank(topHashieRank);
      } else {
        setHashieRank(null);
      }
      
      // TOP 10에 포함된 하시에 제품 수
      const inTop10 = allHashieProducts.filter(p => p.ranking <= 10).length;
      setHashieInTop10(inTop10);
      
      setLoading(false);
    } catch (error) {
      console.error('데이터 로딩 오류:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">데이터 로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="container">
      {/* 헤더 */}
      <header className="header">
        <h1>W CONCEPT 베스트 제품 추적</h1>
        <div className="stats-summary">
          <div className="stat-item">
            <div className="stat-label">총 제품</div>
            <div className="stat-value">{stats?.total_products || 0}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">총 브랜드</div>
            <div className="stat-value">{stats?.total_brands || 0}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">수집 횟수</div>
            <div className="stat-value">{stats?.total_collections || 0}</div>
          </div>
          <div className="stat-item hashie-rank">
            <div className="stat-label">🎯 하시에 (5개)</div>
            <div className="stat-value">
              {hashieRank ? `최고 ${hashieRank}위` : '순위 없음'}
            </div>
            {hashieProducts.length > 0 && (
              <div className="stat-detail">
                TOP 10: {hashieInTop10}개
              </div>
            )}
          </div>
        </div>
      </header>

      {/* 메인 컨텐츠 */}
      <div className="content">
        {/* 왼쪽: 제품 순위 */}
        <div className="section">
          <h2>TOP 10 제품</h2>
          <div className="product-list">
            {products.map((product, index) => (
              <div 
                key={product.product_id} 
                className={`product-item ${product.brand_name === '하시에' ? 'hashie-product' : ''}`}
              >
                <div className="product-rank">{index + 1}</div>
                <div className="product-info">
                  <div className="product-brand">
                    {product.brand_name}
                    {product.brand_name === '하시에' && <span className="hashie-badge"> 🎯 우리 제품</span>}
                  </div>
                  <div className="product-name">{product.product_name}</div>
                  <div className="product-price">
                    ₩{product.price.toLocaleString()}
                    {product.discount_rate && (
                      <span className="discount"> -{product.discount_rate}%</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* 하시에 제품 전체 표시 (TOP 10 밖) */}
          {hashieProducts.length > 0 && (
            <div className="hashie-separate-section">
              <h3>🎯 우리 제품 (하시에) - 총 {hashieProducts.length}개</h3>
              <div className="product-list">
                {hashieProducts
                  .filter(p => p.ranking > 10) // TOP 10 밖의 제품만
                  .sort((a, b) => a.ranking - b.ranking) // 순위순 정렬
                  .map(product => (
                    <div key={product.product_id} className="product-item hashie-product">
                      <div className="product-rank">{product.ranking}</div>
                      <div className="product-info">
                        <div className="product-brand">
                          {product.brand_name}
                          <span className="hashie-badge"> 🎯 우리 제품</span>
                        </div>
                        <div className="product-name">{product.product_name}</div>
                        <div className="product-price">
                          ₩{product.price.toLocaleString()}
                          {product.discount_rate && (
                            <span className="discount"> -{product.discount_rate}%</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
              {hashieProducts.filter(p => p.ranking > 10).length === 0 && (
                <div className="hashie-all-in-top10">
                  ✅ 모든 하시에 제품이 TOP 10에 포함되어 있습니다!
                </div>
              )}
            </div>
          )}
        </div>

        {/* 오른쪽: 브랜드 통계 */}
        <div className="section">
          <h2>브랜드별 제품 수</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={brands}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="brand_name" tick={{fontSize: 11}} angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip 
                  contentStyle={{backgroundColor: '#000', border: '1px solid #333', color: '#fff'}}
                  cursor={{fill: '#222'}}
                />
                <Bar dataKey="product_count" fill="#fff" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <h2 style={{marginTop: '40px'}}>브랜드 통계</h2>
          <div className="brand-table">
            <table>
              <thead>
                <tr>
                  <th>브랜드</th>
                  <th>제품 수</th>
                  <th>평균 가격</th>
                  <th>평균 할인율</th>
                </tr>
              </thead>
              <tbody>
                {brands.map(brand => (
                  <tr key={brand.brand_name}>
                    <td>{brand.brand_name}</td>
                    <td>{brand.product_count}</td>
                    <td>₩{Math.round(brand.avg_price).toLocaleString()}</td>
                    <td>{brand.avg_discount_rate ? `${brand.avg_discount_rate.toFixed(1)}%` : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* 푸터 */}
      <footer className="footer">
        <div>마지막 업데이트: {stats?.latest_collection ? new Date(stats.latest_collection).toLocaleString('ko-KR') : '-'}</div>
        <div>자동 새로고침: 30분마다</div>
      </footer>
    </div>
  );
}

export default App;
