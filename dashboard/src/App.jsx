import { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

// API URL - 환경 변수 또는 기본값 사용
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'https://w-best-tracker.fly.dev';

// 서울 시간(KST) 포맷팅 함수
const formatKST = (dateString) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleString('ko-KR', { 
    timeZone: 'Asia/Seoul',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });
};

// 순위 변동 표시 컴포넌트
const RankingChangeBadge = ({ change, isNew }) => {
  // NEW 배지 우선 표시
  if (isNew) {
    return (
      <span style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '2px 8px',
        borderRadius: '12px',
        fontSize: '11px',
        fontWeight: 'bold',
        background: '#FFD700',
        color: '#000',
        marginLeft: '8px',
        animation: 'pulse 2s infinite'
      }}>
        ✨ NEW
      </span>
    );
  }
  
  if (!change) return null;
  
  const isUp = change.change_type === '상승' || change.change_type === 'up';
  const diff = Math.abs(change.ranking_diff);
  
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      padding: '2px 8px',
      borderRadius: '12px',
      fontSize: '11px',
      fontWeight: 'bold',
      background: isUp ? '#e8f5e9' : '#ffebee',
      color: isUp ? '#2e7d32' : '#c62828',
      marginLeft: '8px'
    }}>
      {isUp ? '↑' : '↓'} {diff}
    </span>
  );
};

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
  const [selectedBrandProducts, setSelectedBrandProducts] = useState(null);
  const [showBrandProducts, setShowBrandProducts] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [productTrend, setProductTrend] = useState(null);
  const [showProductTrend, setShowProductTrend] = useState(false);
  const [productTrendDays, setProductTrendDays] = useState(7);
  const [categoryUpdateTimes, setCategoryUpdateTimes] = useState({});
  const [brandSearchQuery, setBrandSearchQuery] = useState('');
  const [isCrawling, setIsCrawling] = useState(false);
  const [crawlMessage, setCrawlMessage] = useState('');
  const [topProductLimit, setTopProductLimit] = useState(100);
  const [rankingChanges, setRankingChanges] = useState({});

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
    // 카테고리 변경 시 선택된 브랜드 초기화
    setSelectedBrands([]);
    fetchData();
  }, [selectedCategory, topProductLimit]);

  // 매 시간 16분에 자동 업데이트
  useEffect(() => {
    const scheduleNextUpdate = () => {
      const now = new Date();
      const targetMinute = 16;
      const currentMinute = now.getMinutes();
      const currentHour = now.getHours();
      
      let nextUpdate;
      if (currentMinute < targetMinute) {
        // 이번 시간 16분
        nextUpdate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), currentHour, targetMinute, 0);
      } else {
        // 다음 시간 16분
        nextUpdate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), currentHour + 1, targetMinute, 0);
      }
      
      const delay = nextUpdate.getTime() - now.getTime();
      console.log(`다음 업데이트: ${nextUpdate.toLocaleString('ko-KR')} (${Math.round(delay/1000/60)}분 후)`);
      
      const timeout = setTimeout(() => {
        fetchData();
        scheduleNextUpdate(); // 다음 업데이트 예약
      }, delay);
      
      return timeout;
    };
    
    const timeout = scheduleNextUpdate();
    return () => clearTimeout(timeout);
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

  // Export 함수
  const exportToCSV = () => {
    const csvData = products.map(product => ({
      '순위': product.ranking,
      '브랜드': product.brand_name,
      '제품명': product.product_name,
      '카테고리': product.category || '',
      '가격': product.price,
      '할인율': product.discount_rate ? `${product.discount_rate}%` : '',
      '제품URL': product.product_url || '',
      '수집시간': formatKST(product.collected_at)
    }));

    const headers = Object.keys(csvData[0]);
    const csvContent = [
      headers.join(','),
      ...csvData.map(row => headers.map(header => `"${row[header]}"`).join(','))
    ].join('\n');

    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `wconcept_top${topProductLimit}_${new Date().toISOString().slice(0,10)}.csv`;
    link.click();
  };

  const exportToJSON = () => {
    const jsonData = products.map(product => ({
      ranking: product.ranking,
      brand_name: product.brand_name,
      product_name: product.product_name,
      category: product.category,
      price: product.price,
      discount_rate: product.discount_rate,
      product_url: product.product_url,
      image_url: product.image_url,
      collected_at: product.collected_at,
      ranking_change: rankingChanges[product.product_id] || null
    }));

    const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `wconcept_top${topProductLimit}_${new Date().toISOString().slice(0,10)}.json`;
    link.click();
  };

  const fetchData = async () => {
    try {
      const categoryParam = selectedCategory !== 'all' ? `&category=${selectedCategory}` : '';
      const [productsRes, allProductsRes, statsRes, categoryTimesRes] = await Promise.all([
        axios.get(`${API_BASE}/api/products/current?limit=${topProductLimit}${categoryParam}`),
        axios.get(`${API_BASE}/api/products/current?limit=200${categoryParam}`),
        axios.get(`${API_BASE}/api/health`),
        axios.get(`${API_BASE}/api/categories/update-times`)
      ]);
      setProducts(productsRes.data);
      setAllProducts(allProductsRes.data);
      setStats(statsRes.data);
      setCategoryUpdateTimes(categoryTimesRes.data.categories || {});
      
      // 배치 API로 모든 제품의 히스토리를 한 번에 조회
      const productsToTrack = [...productsRes.data];
      
      const changesMap = {};
      const newProducts = new Set();
      
      console.log(`순위 변동 조회 시작 (배치 API - ${productsToTrack.length}개)...`);
      const startTime = Date.now();
      
      try {
        const batchHistoryRes = await axios.post(`${API_BASE}/api/products/batch/history`, {
          product_ids: productsToTrack.map(p => p.product_id),
          days: 2
        });
        
        const histories = batchHistoryRes.data.data;
        
        // 각 제품의 히스토리 분석
        for (const product of productsToTrack) {
          const history = histories[product.product_id] || [];
          
          if (history.length === 0 || history.length === 1) {
            newProducts.add(product.product_id);
          } else if (history.length >= 2) {
            const current = history[0];
            const previous = history[1];
            
            if (current.ranking !== previous.ranking) {
              const diff = previous.ranking - current.ranking;
              changesMap[product.product_id] = {
                old_ranking: previous.ranking,
                new_ranking: current.ranking,
                ranking_diff: diff,
                change_type: diff > 0 ? 'up' : 'down'
              };
            }
          }
        }
        
        const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
        console.log(`✅ 순위 변동 조회 완료: ${elapsedTime}초 (배치 API)`);
        console.log('순위 변동 개수:', Object.keys(changesMap).length);
        console.log('신규 제품 개수:', newProducts.size);
        
      } catch (error) {
        console.warn('배치 API 실패, 개별 조회로 폴백:', error.message);
        
        // Fallback: 개별 조회 (10개씩 배치)
        const batchSize = 10;
        for (let i = 0; i < productsToTrack.length; i += batchSize) {
          const batch = productsToTrack.slice(i, i + batchSize);
          
          await Promise.all(batch.map(async (product) => {
            try {
              const historyRes = await axios.get(`${API_BASE}/api/products/${product.product_id}/history?days=2`);
              const history = historyRes.data;
              
              if (history.length === 0 || history.length === 1) {
                newProducts.add(product.product_id);
              } else if (history.length >= 2) {
                const current = history[0];
                const previous = history[1];
                
                if (current.ranking !== previous.ranking) {
                  const diff = previous.ranking - current.ranking;
                  changesMap[product.product_id] = {
                    old_ranking: previous.ranking,
                    new_ranking: current.ranking,
                    ranking_diff: diff,
                    change_type: diff > 0 ? 'up' : 'down'
                  };
                }
              }
            } catch (err) {
              // 조용히 실패
            }
          }));
        }
        
        const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
        console.log(`✅ 순위 변동 조회 완료: ${elapsedTime}초 (폴백 모드)`);
        console.log('순위 변동 개수:', Object.keys(changesMap).length);
        console.log('신규 제품 개수:', newProducts.size);
      }
      
      setRankingChanges({ ...changesMap, _newProducts: newProducts });
      
      // 현재 카테고리의 브랜드 통계 계산
      const brandStatsMap = {};
      allProductsRes.data.forEach(product => {
        const brand = product.brand_name;
        if (!brand || brand === 'N/A') return;
        
        if (!brandStatsMap[brand]) {
          brandStatsMap[brand] = {
            brand_name: brand,
            product_count: 0,
            total_price: 0,
            total_discount: 0,
            products_with_discount: 0,
            rankings: []
          };
        }
        
        brandStatsMap[brand].product_count++;
        brandStatsMap[brand].total_price += product.price;
        brandStatsMap[brand].rankings.push(product.ranking);
        
        if (product.discount_rate) {
          brandStatsMap[brand].total_discount += product.discount_rate;
          brandStatsMap[brand].products_with_discount++;
        }
      });
      
      // 브랜드 통계 객체로 변환
      const brandStatsArray = Object.values(brandStatsMap).map(stat => ({
        brand_name: stat.brand_name,
        product_count: stat.product_count,
        avg_price: stat.total_price / stat.product_count,
        avg_discount_rate: stat.products_with_discount > 0 
          ? stat.total_discount / stat.products_with_discount 
          : null,
        min_ranking: Math.min(...stat.rankings),
        max_ranking: Math.max(...stat.rankings),
        total_value: stat.total_price,
        last_updated: new Date().toISOString()
      }));
      
      // 제품 수로 정렬
      brandStatsArray.sort((a, b) => b.product_count - a.product_count);
      
      // Top 20만 저장
      setBrands(brandStatsArray.slice(0, 20));
      
      // 현재 카테고리의 브랜드 목록 추출 (중복 제거)
      const uniqueBrands = [...new Set(allProductsRes.data.map(p => p.brand_name))].filter(b => b && b !== 'N/A').sort();
      setAllBrandsList(uniqueBrands);
      
      // 하시에 제품 찾기 (카테고리 필터 적용)
      let allHashieProducts;
      if (selectedCategory === 'all') {
        // 전체 카테고리 선택 시 모든 제품에서 하시에 제품 가져오기
        const allCategoriesRes = await axios.get(`${API_BASE}/api/products/current?limit=10000`);
        allHashieProducts = allCategoriesRes.data.filter(p => p.brand_name === '하시에');
      } else {
        // 특정 카테고리 선택 시 해당 카테고리의 하시에 제품만
        allHashieProducts = allProductsRes.data.filter(p => p.brand_name === '하시에');
      }
      
      // 하시에 제품의 순위 변동도 추적 (TOP 100에 없어도) - 배치 API
      const hashieProductsToTrack = allHashieProducts.filter(
        hp => !productsToTrack.find(p => p.product_id === hp.product_id)
      );
      
      if (hashieProductsToTrack.length > 0) {
        console.log(`하시에 제품 순위 변동 추적 (배치 API - ${hashieProductsToTrack.length}개)...`);
        const hashieStartTime = Date.now();
        
        try {
          const hashieBatchRes = await axios.post(`${API_BASE}/api/products/batch/history`, {
            product_ids: hashieProductsToTrack.map(p => p.product_id),
            days: 2
          });
          
          const hashieHistories = hashieBatchRes.data.data;
          
          for (const hashieProduct of hashieProductsToTrack) {
            const history = hashieHistories[hashieProduct.product_id] || [];
            
            if (history.length === 0 || history.length === 1) {
              newProducts.add(hashieProduct.product_id);
            } else if (history.length >= 2) {
              const current = history[0];
              const previous = history[1];
              
              if (current.ranking !== previous.ranking) {
                const diff = previous.ranking - current.ranking;
                changesMap[hashieProduct.product_id] = {
                  old_ranking: previous.ranking,
                  new_ranking: current.ranking,
                  ranking_diff: diff,
                  change_type: diff > 0 ? 'up' : 'down'
                };
              }
            }
          }
          
          const hashieElapsed = ((Date.now() - hashieStartTime) / 1000).toFixed(2);
          console.log(`✅ 하시에 제품 조회 완료: ${hashieElapsed}초 (배치 API)`);
          
        } catch (error) {
          console.warn('하시에 배치 API 실패, 개별 조회로 폴백:', error.message);
          
          // Fallback: 개별 조회
          await Promise.all(hashieProductsToTrack.map(async (hashieProduct) => {
            try {
              const historyRes = await axios.get(`${API_BASE}/api/products/${hashieProduct.product_id}/history?days=2`);
              const history = historyRes.data;
              
              if (history.length === 0 || history.length === 1) {
                newProducts.add(hashieProduct.product_id);
              } else if (history.length >= 2) {
                const current = history[0];
                const previous = history[1];
                
                if (current.ranking !== previous.ranking) {
                  const diff = previous.ranking - current.ranking;
                  changesMap[hashieProduct.product_id] = {
                    old_ranking: previous.ranking,
                    new_ranking: current.ranking,
                    ranking_diff: diff,
                    change_type: diff > 0 ? 'up' : 'down'
                  };
                }
              }
            } catch (err) {
              // 조용히 실패
            }
          }));
          
          const hashieElapsed = ((Date.now() - hashieStartTime) / 1000).toFixed(2);
          console.log(`✅ 하시에 제품 조회 완료: ${hashieElapsed}초 (폴백 모드)`);
        }
      }
      
      // 업데이트된 변동 데이터 재설정
      setRankingChanges({ ...changesMap, _newProducts: newProducts });
      
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

  const selectAllBrands = () => {
    setSelectedBrands([...allBrandsList]);
  };

  const handleBrandClick = (brandName) => {
    const brandProducts = allProducts.filter(p => p.brand_name === brandName);
    setSelectedBrandProducts({
      brandName,
      products: brandProducts
    });
    setShowBrandProducts(true);
  };

  const handleProductTrendClick = async (product) => {
    try {
      const res = await axios.get(`${API_BASE}/api/trends/product/${product.product_id}?days=${productTrendDays}`);
      setProductTrend({
        product: product,
        data: res.data.data
      });
      setShowProductTrend(true);
    } catch (error) {
      console.error('제품 트렌드 로딩 오류:', error);
      alert('가격 변화 데이터를 불러올 수 없습니다.');
    }
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

  const categories = [
    { key: 'all', name: '전체' },
    { key: 'outer', name: '아우터' },
    { key: 'dress', name: '원피스' },
    { key: 'blouse', name: '블라우스' },
    { key: 'shirt', name: '셔츠' },
    { key: 'tshirt', name: '티셔츠' },
    { key: 'knit', name: '니트' },
    { key: 'skirt', name: '스커트' },
    { key: 'underwear', name: '언더웨어' }
  ];

  return (
    <div className="container">
      {/* 헤더 */}
      <header className="header">
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
          <h1 style={{margin: 0}}>W CONCEPT 베스트 제품 추적</h1>
          
          {/* Export 버튼 */}
          <div style={{display: 'flex', gap: '10px'}}>
            <button
              onClick={exportToCSV}
              style={{
                padding: '8px 16px',
                background: '#4CAF50',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: 'bold',
                fontSize: '13px'
              }}
            >
              📥 CSV 내보내기
            </button>
            <button
              onClick={exportToJSON}
              style={{
                padding: '8px 16px',
                background: '#2196F3',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: 'bold',
                fontSize: '13px'
              }}
            >
              📥 JSON 내보내기
            </button>
          </div>
        </div>
        
        {/* TOP 제품 개수 선택 */}
        <div style={{marginBottom: '15px'}}>
          <label style={{marginRight: '10px', fontWeight: 'bold'}}>표시할 제품 수:</label>
          <select 
            value={topProductLimit}
            onChange={(e) => setTopProductLimit(Number(e.target.value))}
            style={{
              padding: '6px 12px',
              background: '#fff',
              border: '2px solid #ddd',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            <option value={10}>TOP 10</option>
            <option value={20}>TOP 20</option>
            <option value={50}>TOP 50</option>
            <option value={100}>TOP 100</option>
          </select>
        </div>
        
        {/* 카테고리 선택 */}
        <div className="category-selector" style={{
          display: 'flex',
          gap: '10px',
          marginBottom: '20px',
          flexWrap: 'wrap'
        }}>
          {categories.map(cat => (
            <button
              key={cat.key}
              onClick={() => setSelectedCategory(cat.key)}
              style={{
                padding: '8px 16px',
                background: selectedCategory === cat.key ? '#000' : '#fff',
                color: selectedCategory === cat.key ? '#fff' : '#000',
                border: selectedCategory === cat.key ? '2px solid #000' : '1px solid #ddd',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: selectedCategory === cat.key ? 'bold' : 'normal',
                transition: 'all 0.2s'
              }}
            >
              {cat.name}
            </button>
          ))}
        </div>

        {/* 수동 크롤링 버튼 */}
        <div style={{
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '15px'
        }}>
          <button
            onClick={async () => {
              if (isCrawling) {
                alert('이미 크롤링이 진행 중입니다.');
                return;
              }

              const confirmed = window.confirm(
                '수동 크롤링을 시작하시겠습니까?\n약 3-5분 정도 소요됩니다.'
              );

              if (!confirmed) return;

              setIsCrawling(true);
              setCrawlMessage('크롤링 시작 중...');

              try {
                const response = await axios.post(`${API_BASE}/api/crawl/trigger`);
                setCrawlMessage('✅ 크롤링이 시작되었습니다! 3-5분 후 데이터가 업데이트됩니다.');
                
                setTimeout(() => {
                  fetchData();
                  setCrawlMessage('');
                  setIsCrawling(false);
                }, 5 * 60 * 1000);
                
              } catch (error) {
                console.error('크롤링 트리거 오류:', error);
                setCrawlMessage('❌ 크롤링 시작 실패: ' + (error.response?.data?.detail || error.message));
                setIsCrawling(false);
              }
            }}
            disabled={isCrawling}
            style={{
              padding: '10px 20px',
              background: isCrawling ? '#ccc' : '#4CAF50',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              cursor: isCrawling ? 'not-allowed' : 'pointer',
              fontWeight: 'bold',
              fontSize: '14px',
              transition: 'all 0.2s'
            }}
          >
            {isCrawling ? '⏳ 크롤링 중...' : '🔄 수동 크롤링'}
          </button>
          {crawlMessage && (
            <span style={{
              padding: '8px 12px',
              background: crawlMessage.includes('✅') ? '#e8f5e9' : '#ffebee',
              color: crawlMessage.includes('✅') ? '#2e7d32' : '#c62828',
              borderRadius: '4px',
              fontSize: '13px'
            }}>
              {crawlMessage}
            </span>
          )}
        </div>

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
          <h2>TOP {topProductLimit} 제품</h2>
          <div className="product-list">
            {products.map((product, index) => (
              <div 
                key={product.product_id} 
                className={`product-item ${product.brand_name === '하시에' ? 'hashie-product' : ''}`}
                style={{display: 'flex', gap: '15px', alignItems: 'center'}}
              >
                <div className="product-rank">{index + 1}</div>
                
                {/* 제품 썸네일 이미지 */}
                {product.image_url && product.image_url !== 'N/A' && (
                  <img 
                    src={product.image_url} 
                    alt={product.product_name}
                    style={{
                      width: '80px',
                      height: '80px',
                      objectFit: 'cover',
                      borderRadius: '8px',
                      border: '1px solid #e0e0e0'
                    }}
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                )}
                
                <div className="product-info" style={{flex: 1}}>
                  <div className="product-brand">
                    {product.brand_name}
                    {product.brand_name === '하시에' && <span className="hashie-badge"> 🎯 우리 제품</span>}
                    {product.category && <span style={{fontSize: '11px', marginLeft: '8px', color: '#666'}}>({product.category})</span>}
                    <RankingChangeBadge 
                      change={rankingChanges[product.product_id]} 
                      isNew={rankingChanges._newProducts?.has(product.product_id)}
                    />
                  </div>
                  <div className="product-name">{product.product_name}</div>
                  <div className="product-price">
                    ₩{product.price.toLocaleString()}
                    {product.discount_rate && (
                      <span className="discount"> -{product.discount_rate}%</span>
                    )}
                  </div>
                  <div style={{display: 'flex', gap: '8px', marginTop: '8px', flexWrap: 'wrap'}}>
                    {product.product_url && product.product_url !== 'N/A' && (
                      <a 
                        href={product.product_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{
                          display: 'inline-block',
                          padding: '4px 10px',
                          background: '#000',
                          color: '#fff',
                          fontSize: '11px',
                          borderRadius: '4px',
                          textDecoration: 'none',
                          fontWeight: 'bold'
                        }}
                      >
                        제품 바로가기 →
                      </a>
                    )}
                    <button
                      onClick={() => handleProductTrendClick(product)}
                      style={{
                        padding: '4px 10px',
                        background: product.brand_name === '하시에' ? '#4CAF50' : '#2196F3',
                        color: '#fff',
                        fontSize: '11px',
                        borderRadius: '4px',
                        border: 'none',
                        cursor: 'pointer',
                        fontWeight: 'bold'
                      }}
                    >
                      📊 가격/순위 변화
                    </button>
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
                    <div key={product.product_id} className="product-item hashie-product" style={{display: 'flex', gap: '15px', alignItems: 'center'}}>
                      <div className="product-rank">{product.ranking}</div>
                      
                      {/* 제품 썸네일 이미지 */}
                      {product.image_url && product.image_url !== 'N/A' && (
                        <img 
                          src={product.image_url} 
                          alt={product.product_name}
                          style={{
                            width: '80px',
                            height: '80px',
                            objectFit: 'cover',
                            borderRadius: '8px',
                            border: '1px solid #e0e0e0'
                          }}
                          onError={(e) => {
                            e.target.style.display = 'none';
                          }}
                        />
                      )}
                      
                      <div className="product-info" style={{flex: 1}}>
                        <div className="product-brand">
                          {product.brand_name}
                          <span className="hashie-badge"> 🎯 우리 제품</span>
                          {product.category && <span style={{fontSize: '11px', marginLeft: '8px', color: '#333'}}>({product.category})</span>}
                          <RankingChangeBadge 
                            change={rankingChanges[product.product_id]} 
                            isNew={rankingChanges._newProducts?.has(product.product_id)}
                          />
                        </div>
                        <div className="product-name">{product.product_name}</div>
                        <div className="product-price">
                          ₩{product.price.toLocaleString()}
                          {product.discount_rate && (
                            <span className="discount"> -{product.discount_rate}%</span>
                          )}
                        </div>
                        <div style={{display: 'flex', gap: '8px', marginTop: '8px', flexWrap: 'wrap'}}>
                          {product.product_url && product.product_url !== 'N/A' && (
                            <a 
                              href={product.product_url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              style={{
                                display: 'inline-block',
                                padding: '4px 10px',
                                background: '#000',
                                color: '#fff',
                                fontSize: '11px',
                                borderRadius: '4px',
                                textDecoration: 'none',
                                fontWeight: 'bold'
                              }}
                            >
                              제품 바로가기 →
                            </a>
                          )}
                          <button
                            onClick={() => handleProductTrendClick(product)}
                            style={{
                              padding: '4px 10px',
                              background: '#4CAF50',
                              color: '#fff',
                              fontSize: '11px',
                              borderRadius: '4px',
                              border: 'none',
                              cursor: 'pointer',
                              fontWeight: 'bold'
                            }}
                          >
                            📊 가격/순위 변화
                          </button>
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
                background: '#000',
                color: '#fff',
                border: '2px solid #000',
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
              background: '#f5f5f5',
              padding: '15px',
              borderRadius: '8px',
              marginBottom: '20px'
            }}>
              <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '10px', alignItems: 'center'}}>
                <span style={{fontWeight: 'bold'}}>브랜드 선택:</span>
                <div style={{display: 'flex', gap: '8px'}}>
                  <button 
                    onClick={selectAllBrands}
                    style={{
                      padding: '4px 12px',
                      background: '#4CAF50',
                      color: '#fff',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '12px',
                      fontWeight: 'bold'
                    }}
                  >
                    전체 선택
                  </button>
                  <button 
                    onClick={clearBrandSelection}
                    style={{
                      padding: '4px 12px',
                      background: '#ff4444',
                      color: '#fff',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '12px',
                      fontWeight: 'bold'
                    }}
                  >
                    전체 해제
                  </button>
                </div>
              </div>
              
              {/* 브랜드 검색창 */}
              <div style={{marginBottom: '12px'}}>
                <input
                  type="text"
                  placeholder="🔍 브랜드 검색..."
                  value={brandSearchQuery}
                  onChange={(e) => setBrandSearchQuery(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    border: '2px solid #ddd',
                    borderRadius: '6px',
                    fontSize: '14px',
                    outline: 'none',
                    transition: 'border-color 0.2s',
                    boxSizing: 'border-box'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#2196F3'}
                  onBlur={(e) => e.target.style.borderColor = '#ddd'}
                />
                {brandSearchQuery && (
                  <div style={{marginTop: '6px', fontSize: '12px', color: '#666'}}>
                    검색 결과: {allBrandsList.filter(b => b.toLowerCase().includes(brandSearchQuery.toLowerCase())).length}개
                  </div>
                )}
              </div>
              
              <div style={{
                display: 'flex', 
                flexWrap: 'wrap', 
                gap: '8px',
                maxHeight: '400px',
                overflowY: 'auto',
                padding: '5px'
              }}>
                {allBrandsList
                  .filter(brandName => brandName.toLowerCase().includes(brandSearchQuery.toLowerCase()))
                  .map(brandName => (
                  <label 
                    key={brandName}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      padding: '6px 12px',
                      background: selectedBrands.includes(brandName) ? '#000' : '#fff',
                      color: selectedBrands.includes(brandName) ? '#fff' : '#000',
                      border: '1px solid #ddd',
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
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                <XAxis dataKey="brand_name" tick={{fontSize: 11}} angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip 
                  contentStyle={{backgroundColor: '#fff', border: '1px solid #ddd', color: '#000'}}
                  cursor={{fill: '#f5f5f5'}}
                />
                <Bar dataKey="product_count" fill="#000" />
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
                  <tr 
                    key={brand.brand_name}
                    onClick={() => handleBrandClick(brand.brand_name)}
                    style={{cursor: 'pointer'}}
                  >
                    <td style={{fontWeight: 'bold'}}>{brand.brand_name} 👉</td>
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

      {/* 브랜드 제품 목록 모달 */}
      {showBrandProducts && selectedBrandProducts && (
        <div 
          className="modal-overlay"
          onClick={() => setShowBrandProducts(false)}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000
          }}
        >
          <div 
            className="modal-content"
            onClick={(e) => e.stopPropagation()}
            style={{
              background: '#fff',
              border: '2px solid #000',
              borderRadius: '8px',
              padding: '30px',
              maxWidth: '900px',
              maxHeight: '80vh',
              overflow: 'auto',
              width: '90%'
            }}
          >
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
              <h2 style={{margin: 0}}>
                {selectedBrandProducts.brandName} 제품 목록
                <span style={{fontSize: '14px', color: '#888', marginLeft: '10px'}}>
                  (총 {selectedBrandProducts.products.length}개)
                </span>
              </h2>
              <button 
                onClick={() => setShowBrandProducts(false)}
                style={{
                  padding: '8px 16px',
                  background: '#000',
                  color: '#fff',
                  border: '2px solid #000',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontWeight: 'bold'
                }}
              >
                닫기 ✕
              </button>
            </div>

            <div className="product-list" style={{display: 'flex', flexDirection: 'column', gap: '10px'}}>
              {selectedBrandProducts.products
                .sort((a, b) => a.ranking - b.ranking)
                .map(product => (
                  <div 
                    key={product.product_id} 
                    className="product-item"
                    style={{
                      display: 'flex',
                      gap: '15px',
                      border: '1px solid #ddd',
                      padding: '15px',
                      background: '#fff',
                      alignItems: 'center'
                    }}
                  >
                    <div className="product-rank" style={{
                      fontSize: '18px',
                      fontWeight: 'bold',
                      minWidth: '50px',
                      textAlign: 'center',
                      borderRight: '1px solid #ddd',
                      paddingRight: '15px'
                    }}>
                      #{product.ranking}
                    </div>
                    
                    {/* 제품 썸네일 이미지 */}
                    {product.image_url && product.image_url !== 'N/A' && (
                      <img 
                        src={product.image_url} 
                        alt={product.product_name}
                        style={{
                          width: '80px',
                          height: '80px',
                          objectFit: 'cover',
                          borderRadius: '8px',
                          border: '1px solid #e0e0e0'
                        }}
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    )}
                    
                    <div style={{flex: 1}}>
                      <div style={{fontSize: '14px', fontWeight: 'bold', marginBottom: '5px'}}>
                        {product.product_name}
                        <RankingChangeBadge 
                          change={rankingChanges[product.product_id]} 
                          isNew={rankingChanges._newProducts?.has(product.product_id)}
                        />
                      </div>
                      <div style={{fontSize: '16px', fontWeight: 'bold', marginBottom: '10px'}}>
                        ₩{product.price.toLocaleString()}
                        {product.discount_rate && (
                          <span style={{
                            color: '#fff',
                            background: '#f44336',
                            border: '1px solid #d32f2f',
                            padding: '2px 8px',
                            fontSize: '12px',
                            marginLeft: '8px',
                            borderRadius: '4px'
                          }}>
                            -{product.discount_rate}%
                          </span>
                        )}
                      </div>
                      <div style={{display: 'flex', gap: '8px', flexWrap: 'wrap'}}>
                        {product.product_url && product.product_url !== 'N/A' && (
                          <a 
                            href={product.product_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            style={{
                              display: 'inline-block',
                              padding: '6px 12px',
                              background: '#000',
                              color: '#fff',
                              fontSize: '12px',
                              borderRadius: '4px',
                              textDecoration: 'none',
                              fontWeight: 'bold'
                            }}
                          >
                            제품 바로가기 →
                          </a>
                        )}
                        <button
                          onClick={() => {
                            setShowBrandProducts(false);
                            handleProductTrendClick(product);
                          }}
                          style={{
                            padding: '6px 12px',
                            background: '#2196F3',
                            color: '#fff',
                            fontSize: '12px',
                            borderRadius: '4px',
                            border: 'none',
                            cursor: 'pointer',
                            fontWeight: 'bold'
                          }}
                        >
                          📊 가격/순위 변화
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}

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
                background: '#fff',
                color: '#000',
                border: '1px solid #ddd',
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
                background: '#fff',
                color: '#000',
                border: '1px solid #ddd',
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
                  <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                  <XAxis 
                    dataKey="collected_at" 
                    tickFormatter={(time) => new Date(time).toLocaleDateString('ko-KR', {timeZone: 'Asia/Seoul', month: 'short', day: 'numeric'})}
                    tick={{fontSize: 11}}
                  />
                  <YAxis reversed domain={['auto', 'auto']} />
                  <Tooltip 
                    contentStyle={{backgroundColor: '#fff', border: '1px solid #ddd', color: '#000'}}
                    labelFormatter={(time) => formatKST(time)}
                    formatter={(value) => [value?.toFixed(1), '평균 순위']}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="avg_ranking" 
                    stroke="#2196F3" 
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
                  <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                  <XAxis 
                    dataKey="collected_at" 
                    tickFormatter={(time) => new Date(time).toLocaleDateString('ko-KR', {timeZone: 'Asia/Seoul', month: 'short', day: 'numeric'})}
                    tick={{fontSize: 11}}
                  />
                  <YAxis />
                  <Tooltip 
                    contentStyle={{backgroundColor: '#fff', border: '1px solid #ddd', color: '#000'}}
                    labelFormatter={(time) => formatKST(time)}
                    formatter={(value) => [value, '제품 수']}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="product_count" 
                    stroke="#4CAF50" 
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

      {/* 제품 가격/순위 변화 모달 */}
      {showProductTrend && productTrend && (
        <div 
          className="modal-overlay"
          onClick={() => setShowProductTrend(false)}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000
          }}
        >
          <div 
            className="modal-content"
            onClick={(e) => e.stopPropagation()}
            style={{
              background: '#fff',
              border: '2px solid #000',
              borderRadius: '8px',
              padding: '30px',
              maxWidth: '1000px',
              maxHeight: '80vh',
              overflow: 'auto',
              width: '90%'
            }}
          >
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
              <div>
                <h2 style={{margin: 0, color: '#000'}}>
                  📊 {productTrend.product.product_name}
                </h2>
                <p style={{margin: '5px 0', color: '#666', fontSize: '14px'}}>
                  {productTrend.product.brand_name} | {productTrend.product.category}
                </p>
              </div>
              <button 
                onClick={() => setShowProductTrend(false)}
                style={{
                  padding: '8px 16px',
                  background: '#000',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontWeight: 'bold'
                }}
              >
                닫기 ✕
              </button>
            </div>

            <div style={{marginBottom: '20px'}}>
              <label style={{marginRight: '10px', color: '#000'}}>기간:</label>
              <select 
                value={productTrendDays}
                onChange={(e) => {
                  setProductTrendDays(Number(e.target.value));
                  handleProductTrendClick(productTrend.product);
                }}
                style={{
                  padding: '8px 12px',
                  background: '#fff',
                  color: '#000',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                <option value={7}>최근 7일</option>
                <option value={14}>최근 14일</option>
                <option value={30}>최근 30일</option>
              </select>
            </div>

            {productTrend.data && productTrend.data.length > 0 ? (
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px'}}>
                {/* 순위 변화 차트 */}
                <div>
                  <h3 style={{textAlign: 'center', marginBottom: '10px', color: '#000'}}>순위 변화</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={productTrend.data}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#ddd" />
                      <XAxis 
                        dataKey="collected_at" 
                        tickFormatter={(time) => new Date(time).toLocaleDateString('ko-KR', {timeZone: 'Asia/Seoul', month: 'short', day: 'numeric'})}
                        tick={{fontSize: 11, fill: '#000'}}
                      />
                      <YAxis reversed domain={['auto', 'auto']} tick={{fill: '#000'}} />
                      <Tooltip 
                        contentStyle={{backgroundColor: '#fff', border: '1px solid #ddd', color: '#000'}}
                        labelFormatter={(time) => formatKST(time)}
                        formatter={(value) => [value, '순위']}
                      />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="ranking" 
                        stroke="#2196F3" 
                        strokeWidth={2}
                        name="순위"
                        dot={{r: 4}}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                {/* 가격 변화 차트 */}
                <div>
                  <h3 style={{textAlign: 'center', marginBottom: '10px', color: '#000'}}>가격 변화</h3>
                  {(() => {
                    const prices = productTrend.data.map(d => d.price);
                    const hasChange = new Set(prices).size > 1;
                    
                    return hasChange ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={productTrend.data}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#ddd" />
                          <XAxis 
                            dataKey="collected_at" 
                            tickFormatter={(time) => new Date(time).toLocaleDateString('ko-KR', {timeZone: 'Asia/Seoul', month: 'short', day: 'numeric'})}
                            tick={{fontSize: 11, fill: '#000'}}
                          />
                          <YAxis tick={{fill: '#000'}} />
                          <Tooltip 
                            contentStyle={{backgroundColor: '#fff', border: '1px solid #ddd', color: '#000'}}
                            labelFormatter={(time) => formatKST(time)}
                            formatter={(value) => [`₩${value?.toLocaleString()}`, '가격']}
                          />
                          <Legend />
                          <Line 
                            type="monotone" 
                            dataKey="price" 
                            stroke="#4CAF50" 
                            strokeWidth={2}
                            name="판매가"
                            dot={{r: 4}}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <div style={{
                        height: '300px',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        background: '#f5f5f5',
                        borderRadius: '8px',
                        border: '1px solid #ddd'
                      }}>
                        <div style={{fontSize: '48px', marginBottom: '15px'}}>💰</div>
                        <div style={{fontSize: '16px', fontWeight: 'bold', color: '#666', marginBottom: '5px'}}>
                          가격 변동 없음
                        </div>
                        <div style={{fontSize: '24px', fontWeight: 'bold', color: '#4CAF50', marginBottom: '10px'}}>
                          ₩{prices[0]?.toLocaleString()}
                        </div>
                        <div style={{fontSize: '13px', color: '#999'}}>
                          해당 기간 동안 가격이 일정하게 유지되었습니다
                        </div>
                      </div>
                    );
                  })()}
                </div>
              </div>
            ) : (
              <div style={{textAlign: 'center', padding: '40px', color: '#888'}}>
                이 제품의 가격/순위 변화 데이터가 없습니다.
              </div>
            )}
          </div>
        </div>
      )}

      {/* 푸터 */}
      <footer className="footer">
        <div>
          <strong>마지막 업데이트:</strong>{' '}
          {selectedCategory !== 'all' && categoryUpdateTimes[selectedCategory] ? (
            <>
              <span style={{color: '#4CAF50', fontWeight: 'bold'}}>
                {categories.find(c => c.key === selectedCategory)?.name}
              </span>
              {' '}
              {formatKST(categoryUpdateTimes[selectedCategory].latest_collection)}
              {' '}
              <span style={{color: '#888', fontSize: '12px'}}>
                ({categoryUpdateTimes[selectedCategory].product_count}개 제품)
              </span>
            </>
          ) : selectedCategory === 'all' ? (
            <>
              전체 카테고리 {formatKST(stats?.latest_collection)}
              {' '}
              <span style={{color: '#888', fontSize: '12px'}}>
                ({Object.keys(categoryUpdateTimes).length}개 카테고리)
              </span>
            </>
          ) : '-'}
        </div>
        <div>자동 업데이트: 매 시간 16분</div>
      </footer>
    </div>
  );
}

export default App;
