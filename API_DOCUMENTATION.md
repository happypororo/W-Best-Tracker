# W Concept Best Products Tracking - REST API Documentation

## 📚 Overview

This REST API provides comprehensive access to W Concept's best products tracking data, including:
- Real-time product rankings
- Brand statistics and analytics
- Historical price and ranking changes
- Scraping job monitoring

**Base URL**: `https://8000-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai`  
**API Version**: 2.0.0  
**Documentation**: `/api/docs` (Swagger UI)  
**Alternative Docs**: `/api/redoc` (ReDoc)

---

## 🚀 Quick Start

### Using curl
```bash
# Health check
curl https://8000-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai/api/health

# Get top 10 products
curl "https://8000-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai/api/products/current?limit=10"

# Get brand statistics
curl "https://8000-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai/api/brands/stats?limit=5"
```

### Using JavaScript (Fetch API)
```javascript
// Fetch current products
fetch('https://8000-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai/api/products/current?limit=10')
  .then(response => response.json())
  .then(data => console.log(data));

// Fetch brand statistics
fetch('https://8000-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai/api/brands/stats')
  .then(response => response.json())
  .then(data => console.log(data));
```

### Using Python (requests)
```python
import requests

# Get health status
response = requests.get('https://8000-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai/api/health')
print(response.json())

# Get current products
response = requests.get(
    'https://8000-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai/api/products/current',
    params={'limit': 50}
)
products = response.json()
```

---

## 📋 API Endpoints

### 1. System Health

#### `GET /api/health`

Get system status and database statistics.

**Response:**
```json
{
  "status": "healthy",
  "database_connected": true,
  "total_products": 203,
  "total_brands": 90,
  "latest_collection": "2025-10-23T02:10:44.111068",
  "total_collections": 2,
  "api_version": "2.0.0"
}
```

**Status Codes:**
- `200 OK`: System is healthy
- `500 Internal Server Error`: System error

---

### 2. Current Products

#### `GET /api/products/current`

Get the latest product rankings.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 200 | Number of products to return (1-200) |
| `brand` | string | null | Filter by brand name (optional) |

**Example Request:**
```bash
GET /api/products/current?limit=10&brand=프론트로우
```

**Response:**
```json
[
  {
    "product_id": "PROD_307602440",
    "brand_name": "허엄씨",
    "product_name": "[30%쿠폰] [프리오더] 헤이블 퍼카라 하프코트 (2color)",
    "price": 244300,
    "discount_rate": 30.0,
    "image_url": "https://product-image.wconcept.co.kr/...",
    "ranking": 1,
    "collected_at": "2025-10-23T02:10:44.111068"
  }
]
```

**Status Codes:**
- `200 OK`: Success
- `422 Unprocessable Entity`: Invalid parameters
- `500 Internal Server Error`: Server error

---

### 3. Brand Statistics

#### `GET /api/brands/stats`

Get aggregated statistics by brand.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Number of brands to return (1-200) |
| `sort_by` | string | product_count | Sort criterion: `product_count`, `total_value`, `avg_price` |

**Example Request:**
```bash
GET /api/brands/stats?limit=5&sort_by=total_value
```

**Response:**
```json
[
  {
    "brand_name": "프론트로우",
    "product_count": 14,
    "total_value": 3837488,
    "avg_price": 274106.29,
    "avg_discount_rate": 35.57,
    "min_ranking": 37,
    "max_ranking": 37,
    "last_updated": "2025-10-23T02:10:44.111068"
  }
]
```

**Status Codes:**
- `200 OK`: Success
- `422 Unprocessable Entity`: Invalid parameters

---

### 4. Product History

#### `GET /api/products/{product_id}/history`

Get historical data for a specific product.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `product_id` | string | Product ID (e.g., "PROD_307602440") |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | integer | 7 | Number of days to look back (1-30) |

**Example Request:**
```bash
GET /api/products/PROD_307602440/history?days=7
```

**Response:**
```json
[
  {
    "collected_at": "2025-10-23T02:10:44.111068",
    "ranking": 1,
    "price": 244300,
    "discount_rate": 30.0
  }
]
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: Product not found
- `422 Unprocessable Entity`: Invalid parameters

---

### 5. Price Changes

#### `GET /api/price-changes`

Get price change history.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | integer | 7 | Number of days to look back (1-30) |
| `limit` | integer | 50 | Number of changes to return (1-200) |

**Example Request:**
```bash
GET /api/price-changes?days=7&limit=20
```

**Response:**
```json
[
  {
    "product_id": "PROD_123456",
    "brand_name": "브랜드명",
    "product_name": "제품명",
    "old_price": 300000,
    "new_price": 250000,
    "price_diff": -50000,
    "price_diff_percent": -16.67,
    "changed_at": "2025-10-22T15:30:00"
  }
]
```

**Status Codes:**
- `200 OK`: Success
- `422 Unprocessable Entity`: Invalid parameters

---

### 6. Ranking Changes

#### `GET /api/ranking-changes`

Get ranking change history.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | integer | 7 | Number of days to look back (1-30) |
| `change_type` | string | null | Filter by change type: `상승` or `하락` (optional) |
| `limit` | integer | 50 | Number of changes to return (1-200) |

**Example Request:**
```bash
GET /api/ranking-changes?days=7&change_type=상승&limit=20
```

**Response:**
```json
[
  {
    "product_id": "PROD_123456",
    "brand_name": "브랜드명",
    "product_name": "제품명",
    "old_ranking": 10,
    "new_ranking": 5,
    "ranking_diff": -5,
    "change_type": "상승",
    "changed_at": "2025-10-22T15:30:00"
  }
]
```

**Status Codes:**
- `200 OK`: Success
- `422 Unprocessable Entity`: Invalid parameters

---

### 7. Scraping Jobs History

#### `GET /api/jobs/history`

Get scraping job execution history.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Number of jobs to return (1-100) |

**Example Request:**
```bash
GET /api/jobs/history?limit=10
```

**Response:**
```json
[
  {
    "job_id": 2,
    "started_at": "2025-10-23T02:10:35.202661",
    "completed_at": "2025-10-23T02:10:44.124179",
    "status": "success",
    "products_collected": 200,
    "error_message": null,
    "duration_seconds": 8.0
  }
]
```

**Status Codes:**
- `200 OK`: Success
- `422 Unprocessable Entity`: Invalid parameters

---

## 🔧 Error Handling

All endpoints use standard HTTP status codes and return error details in JSON format:

```json
{
  "detail": "Error description here"
}
```

### Common Status Codes
- `200 OK`: Request successful
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Invalid request parameters
- `500 Internal Server Error`: Server error

---

## 📊 Data Models

### Product
```typescript
interface Product {
  product_id: string;
  brand_name: string;
  product_name: string;
  price: number;
  discount_rate: number | null;
  image_url: string;
  ranking: number;
  collected_at: string; // ISO 8601 datetime
}
```

### BrandStats
```typescript
interface BrandStats {
  brand_name: string;
  product_count: number;
  total_value: number;
  avg_price: number;
  avg_discount_rate: number | null;
  min_ranking: number;
  max_ranking: number;
  last_updated: string; // ISO 8601 datetime
}
```

### PriceChange
```typescript
interface PriceChange {
  product_id: string;
  brand_name: string;
  product_name: string;
  old_price: number;
  new_price: number;
  price_diff: number;
  price_diff_percent: number;
  changed_at: string; // ISO 8601 datetime
}
```

### RankingChange
```typescript
interface RankingChange {
  product_id: string;
  brand_name: string;
  product_name: string;
  old_ranking: number;
  new_ranking: number;
  ranking_diff: number;
  change_type: "상승" | "하락";
  changed_at: string; // ISO 8601 datetime
}
```

---

## 🌐 CORS Support

The API supports Cross-Origin Resource Sharing (CORS) for all origins. This allows frontend applications from any domain to access the API.

**CORS Headers:**
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: *`
- `Access-Control-Allow-Headers: *`

---

## 📱 Usage Examples

### React Example

```jsx
import React, { useEffect, useState } from 'react';

function ProductList() {
  const [products, setProducts] = useState([]);
  
  useEffect(() => {
    fetch('https://8000-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai/api/products/current?limit=10')
      .then(res => res.json())
      .then(data => setProducts(data));
  }, []);
  
  return (
    <div>
      {products.map(product => (
        <div key={product.product_id}>
          <h3>#{product.ranking} - {product.product_name}</h3>
          <p>{product.brand_name} - ₩{product.price.toLocaleString()}</p>
        </div>
      ))}
    </div>
  );
}
```

### Vue.js Example

```vue
<template>
  <div>
    <div v-for="brand in brands" :key="brand.brand_name">
      <h3>{{ brand.brand_name }}</h3>
      <p>Products: {{ brand.product_count }}</p>
      <p>Avg Price: ₩{{ brand.avg_price.toLocaleString() }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      brands: []
    };
  },
  async mounted() {
    const response = await fetch(
      'https://8000-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai/api/brands/stats?limit=10'
    );
    this.brands = await response.json();
  }
};
</script>
```

### Node.js/Express Backend Example

```javascript
const express = require('express');
const axios = require('axios');

const app = express();

app.get('/products', async (req, res) => {
  try {
    const response = await axios.get(
      'https://8000-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai/api/products/current',
      { params: { limit: req.query.limit || 50 } }
    );
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000);
```

---

## 🔍 Interactive API Documentation

Visit the interactive API documentation at:

- **Swagger UI**: https://8000-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai/api/docs
- **ReDoc**: https://8000-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai/api/redoc

These interfaces allow you to:
- Explore all available endpoints
- Test API requests directly in the browser
- View request/response schemas
- See example responses

---

## 📈 Performance Considerations

- **Rate Limiting**: Currently no rate limits (recommended to add in production)
- **Caching**: No built-in caching (consider adding Redis for production)
- **Database**: SQLite (consider PostgreSQL for production scale)
- **Pagination**: Use `limit` parameter to control response size

---

## 🔐 Security Notes

**Current Implementation** (Development):
- No authentication required
- CORS allows all origins
- No rate limiting

**Production Recommendations**:
- Add API key authentication
- Restrict CORS to specific domains
- Implement rate limiting
- Use HTTPS only
- Add request validation

---

## 📞 Support

For issues or questions about the API:
1. Check the interactive documentation at `/api/docs`
2. Review this documentation
3. Check the error response details

---

## 🎯 Next Steps

After familiarizing yourself with the API:
1. Build a frontend dashboard (React/Vue)
2. Create data visualizations
3. Set up automated alerts
4. Integrate with external systems

---

**Last Updated**: 2025-10-23  
**API Version**: 2.0.0
