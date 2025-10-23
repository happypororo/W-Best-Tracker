import { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

const API_BASE = 'https://8000-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai';

function App() {
  const [products, setProducts] = useState([]);
  const [brands, setBrands] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000); // 1분마다 갱신
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [productsRes, brandsRes, statsRes] = await Promise.all([
        axios.get(`${API_BASE}/api/products/current?limit=10`),
        axios.get(`${API_BASE}/api/brands/stats?limit=10`),
        axios.get(`${API_BASE}/api/health`)
      ]);
      setProducts(productsRes.data);
      setBrands(brandsRes.data);
      setStats(statsRes.data);
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
        </div>
      </header>

      {/* 메인 컨텐츠 */}
      <div className="content">
        {/* 왼쪽: 제품 순위 */}
        <div className="section">
          <h2>TOP 10 제품</h2>
          <div className="product-list">
            {products.map((product, index) => (
              <div key={product.product_id} className="product-item">
                <div className="product-rank">{index + 1}</div>
                <div className="product-info">
                  <div className="product-brand">{product.brand_name}</div>
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
        <div>자동 새로고침: 1분마다</div>
      </footer>
    </div>
  );
}

export default App;
