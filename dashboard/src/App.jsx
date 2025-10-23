import { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

const API_BASE = 'https://8000-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai';

function App() {
  const [products, setProducts] = useState([]);
  const [allProducts, setAllProducts] = useState([]);
  const [brands, setBrands] = useState([]);
  const [allBrandsList, setAllBrandsList] = useState([]);
  const [selectedBrands, setSelectedBrands] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [hashieRank, setHashieRank] = useState(null);
  const [hashieProducts, setHashieProducts] = useState([]);
  const [hashieInTop10, setHashieInTop10] = useState(0);
  const [showBrandFilter, setShowBrandFilter] = useState(false);
  const [brandTrends, setBrandTrends] = useState({});
  const [selectedTrendBrand, setSelectedTrendBrand] = useState('하시에');
  const [trendDays, setTrendDays] = useState(7);

  // localStorage에서 선택된 브랜드 불러오기
  useEffect(() => {
    const saved = localStorage.getItem('selectedBrands');
    if (saved) {
      try {
        setSelectedBrands(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to load selected brands:', e);
      }
    }
  }, []);

  // 선택된 브랜드가 변경되면 localStorage에 저장
  useEffect(() => {
    if (selectedBrands.length > 0) {
      localStorage.setItem('selectedBrands', JSON.stringify(selectedBrands));
    } else {
      localStorage.removeItem('selectedBrands');
    }
  }, [selectedBrands]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 1800000); // 30분마다 갱신 (30분 = 1800000ms)
    return () => clearInterval(interval);
  }, []);

  // 브랜드 순위 동향 데이터 가져오기
  useEffect(() => {
    if (selectedTrendBrand) {
      fetchBrandTrend(selectedTrendBrand);
    }
  }, [selectedTrendBrand, trendDays]);

  const fetchBrandTrend = async (brandName) => {
    try {
      const res = await axios.get(`${API_BASE}/api/trends/brand/${encodeURIComponent(brandName)}?days=${trendDays}`);
      setBrandTrends(prev => ({
        ...prev,
        [brandName]: res.data.data
      }));
    } catch (error) {
      console.error('브랜드 동향 데이터 로딩 오류:', error);
    }
  };

  const fetchData = async () => {
    try {
      const [productsRes, allProductsRes, brandsRes, statsRes, allBrandsRes] = await Promise.all([
        axios.get(`${API_BASE}/api/products/current?limit=10`),
        axios.get(`${API_BASE}/api/products/current?limit=200`),
        axios.get(`${API_BASE}/api/brands/stats?limit=10`),
        axios.get(`${API_BASE}/api/health`),
        axios.get(`${API_BASE}/api/brands/list`)
      ]);
      setProducts(productsRes.data);
      setAllProducts(allProductsRes.data);
      setBrands(brandsRes.data);
      setStats(statsRes.data);
      setAllBrandsList(allBrandsRes.data);
      
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

  const toggleBrandSelection = (brandName) => {
    setSelectedBrands(prev => {
      if (prev.includes(brandName)) {
        return prev.filter(b => b !== brandName);
      } else {
        return [...prev, brandName];
      }
    });
  };

  const clearBrandSelection = () => {
    setSelectedBrands([]);
  };

  // 필터링된 브랜드 통계
  const filteredBrands = selectedBrands.length > 0
    ? brands.filter(b => selectedBrands.includes(b.brand_name))
    : brands;

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
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
            <h2 style={{margin: 0}}>브랜드별 제품 수</h2>
            <button 
              onClick={() => setShowBrandFilter(!showBrandFilter)}
              className="filter-button"
              style={{
                padding: '8px 16px',
                background: '#fff',
                color: '#000',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              {showBrandFilter ? '필터 닫기' : '브랜드 필터'}
              {selectedBrands.length > 0 && ` (${selectedBrands.length})`}
            </button>
          </div>

          {showBrandFilter && (
            <div className="brand-filter" style={{
              background: '#1a1a1a',
              padding: '15px',
              borderRadius: '8px',
              marginBottom: '20px',
              maxHeight: '200px',
              overflowY: 'auto'
            }}>
              <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '10px'}}>
                <span style={{fontWeight: 'bold'}}>브랜드 선택:</span>
                {selectedBrands.length > 0 && (
                  <button 
                    onClick={clearBrandSelection}
                    style={{
                      padding: '4px 12px',
                      background: '#ff4444',
                      color: '#fff',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '12px'
                    }}
                  >
                    전체 해제
                  </button>
                )}
              </div>
              <div style={{display: 'flex', flexWrap: 'wrap', gap: '8px'}}>
                {allBrandsList.map(brandName => (
                  <label 
                    key={brandName}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      padding: '6px 12px',
                      background: selectedBrands.includes(brandName) ? '#fff' : '#2a2a2a',
                      color: selectedBrands.includes(brandName) ? '#000' : '#fff',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '13px',
                      transition: 'all 0.2s'
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={selectedBrands.includes(brandName)}
                      onChange={() => toggleBrandSelection(brandName)}
                      style={{marginRight: '6px'}}
                    />
                    {brandName}
                  </label>
                ))}
              </div>
            </div>
          )}

          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={filteredBrands}>
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

          <h2 style={{marginTop: '40px'}}>
            브랜드 통계
            {selectedBrands.length > 0 && (
              <span style={{fontSize: '14px', color: '#888', marginLeft: '10px'}}>
                (필터링됨: {selectedBrands.length}개 브랜드)
              </span>
            )}
          </h2>
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
                {filteredBrands.map(brand => (
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

      {/* 순위 동향 차트 섹션 */}
      <div className="section" style={{gridColumn: '1 / -1', marginTop: '40px'}}>
        <h2>📈 순위 동향 차트</h2>
        
        <div style={{display: 'flex', gap: '20px', marginBottom: '20px', alignItems: 'center'}}>
          <div>
            <label style={{marginRight: '10px'}}>브랜드 선택:</label>
            <select 
              value={selectedTrendBrand}
              onChange={(e) => setSelectedTrendBrand(e.target.value)}
              style={{
                padding: '8px 12px',
                background: '#2a2a2a',
                color: '#fff',
                border: '1px solid #444',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              <option value="하시에">하시에</option>
              {allBrandsList.filter(b => b !== '하시에').slice(0, 20).map(brand => (
                <option key={brand} value={brand}>{brand}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label style={{marginRight: '10px'}}>기간:</label>
            <select 
              value={trendDays}
              onChange={(e) => setTrendDays(Number(e.target.value))}
              style={{
                padding: '8px 12px',
                background: '#2a2a2a',
                color: '#fff',
                border: '1px solid #444',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              <option value={7}>최근 7일</option>
              <option value={14}>최근 14일</option>
              <option value={30}>최근 30일</option>
            </select>
          </div>
        </div>

        {brandTrends[selectedTrendBrand] && brandTrends[selectedTrendBrand].length > 0 ? (
          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px'}}>
            {/* 평균 순위 차트 */}
            <div className="chart-container">
              <h3 style={{textAlign: 'center', marginBottom: '10px'}}>평균 순위 변화</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={brandTrends[selectedTrendBrand]}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis 
                    dataKey="collected_at" 
                    tickFormatter={(time) => new Date(time).toLocaleDateString('ko-KR', {month: 'short', day: 'numeric'})}
                    tick={{fontSize: 11}}
                  />
                  <YAxis reversed domain={['auto', 'auto']} />
                  <Tooltip 
                    contentStyle={{backgroundColor: '#000', border: '1px solid #333', color: '#fff'}}
                    labelFormatter={(time) => new Date(time).toLocaleString('ko-KR')}
                    formatter={(value) => [value?.toFixed(1), '평균 순위']}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="avg_ranking" 
                    stroke="#8884d8" 
                    strokeWidth={2}
                    name="평균 순위"
                    dot={{r: 4}}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* 제품 수 차트 */}
            <div className="chart-container">
              <h3 style={{textAlign: 'center', marginBottom: '10px'}}>제품 수 변화</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={brandTrends[selectedTrendBrand]}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis 
                    dataKey="collected_at" 
                    tickFormatter={(time) => new Date(time).toLocaleDateString('ko-KR', {month: 'short', day: 'numeric'})}
                    tick={{fontSize: 11}}
                  />
                  <YAxis />
                  <Tooltip 
                    contentStyle={{backgroundColor: '#000', border: '1px solid #333', color: '#fff'}}
                    labelFormatter={(time) => new Date(time).toLocaleString('ko-KR')}
                    formatter={(value) => [value, '제품 수']}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="product_count" 
                    stroke="#82ca9d" 
                    strokeWidth={2}
                    name="제품 수"
                    dot={{r: 4}}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        ) : (
          <div style={{textAlign: 'center', padding: '40px', color: '#888'}}>
            선택한 브랜드의 동향 데이터가 없습니다.
          </div>
        )}
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
