#!/usr/bin/env python3
"""
W Concept Best Products Tracking - REST API Server
Phase 2: REST API implementation with FastAPI

제공 기능:
1. 현재 순위 조회 (GET /api/products/current)
2. 브랜드 통계 조회 (GET /api/brands/stats)
3. 제품 히스토리 조회 (GET /api/products/{product_id}/history)
4. 가격 변동 조회 (GET /api/price-changes)
5. 순위 변동 조회 (GET /api/ranking-changes)
6. 스크래핑 작업 이력 (GET /api/jobs/history)
7. 시스템 상태 (GET /api/health)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import sqlite3
from contextlib import contextmanager
import json

# FastAPI 앱 초기화
app = FastAPI(
    title="W Concept Best Products Tracking API",
    description="W Concept 베스트 제품 추적 시스템 REST API",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS 설정 (프론트엔드 연동용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 설정
DB_PATH = "wconcept_tracking.db"

@contextmanager
def get_db_connection():
    """데이터베이스 연결 컨텍스트 매니저"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ==================== Pydantic Models ====================

class Product(BaseModel):
    """제품 정보 모델"""
    product_id: str
    brand_name: str
    product_name: str
    price: int
    discount_rate: Optional[float] = None
    image_url: str
    ranking: int
    collected_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "PROD_123456",
                "brand_name": "GENTLE MONSTER",
                "product_name": "선글라스 컬렉션",
                "price": 250000,
                "discount_rate": 15.0,
                "image_url": "https://image.wconcept.co.kr/...",
                "ranking": 1,
                "collected_at": "2024-01-15T09:00:00"
            }
        }


class BrandStats(BaseModel):
    """브랜드 통계 모델"""
    brand_name: str
    product_count: int
    total_value: int
    avg_price: float
    avg_discount_rate: Optional[float] = None
    min_ranking: int
    max_ranking: int
    last_updated: datetime


class PriceChange(BaseModel):
    """가격 변동 모델"""
    product_id: str
    brand_name: str
    product_name: str
    old_price: int
    new_price: int
    price_diff: int
    price_diff_percent: float
    changed_at: datetime


class RankingChange(BaseModel):
    """순위 변동 모델"""
    product_id: str
    brand_name: str
    product_name: str
    old_ranking: int
    new_ranking: int
    ranking_diff: int
    change_type: str  # "상승", "하락"
    changed_at: datetime


class ProductHistory(BaseModel):
    """제품 히스토리 모델"""
    collected_at: datetime
    ranking: int
    price: int
    discount_rate: Optional[float] = None


class ScrapingJob(BaseModel):
    """스크래핑 작업 모델"""
    job_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    products_collected: Optional[int] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None


class HealthStatus(BaseModel):
    """시스템 상태 모델"""
    status: str
    database_connected: bool
    total_products: int
    total_brands: int
    latest_collection: Optional[datetime] = None
    total_collections: int
    api_version: str


# ==================== Helper Functions ====================

def row_to_dict(row: sqlite3.Row) -> Dict:
    """sqlite3.Row를 딕셔너리로 변환"""
    return dict(zip(row.keys(), row))


def format_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """문자열을 datetime 객체로 변환"""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except:
        return None


# ==================== API Endpoints ====================

@app.get("/", tags=["Root"])
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "W Concept Best Products Tracking API",
        "version": "2.0.0",
        "docs": "/api/docs",
        "endpoints": {
            "현재_순위": "/api/products/current",
            "브랜드_목록": "/api/brands/list",
            "브랜드_통계": "/api/brands/stats",
            "브랜드_순위동향": "/api/trends/brand/{brand_name}",
            "제품_순위동향": "/api/trends/product/{product_id}",
            "제품_히스토리": "/api/products/{product_id}/history",
            "가격_변동": "/api/price-changes",
            "순위_변동": "/api/ranking-changes",
            "작업_이력": "/api/jobs/history",
            "시스템_상태": "/api/health"
        }
    }


@app.get("/api/health", response_model=HealthStatus, tags=["System"])
async def health_check():
    """시스템 상태 확인"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 총 제품 수
            cursor.execute("SELECT COUNT(DISTINCT product_id) FROM products")
            total_products = cursor.fetchone()[0]
            
            # 총 브랜드 수
            cursor.execute("SELECT COUNT(DISTINCT brand_name) FROM products")
            total_brands = cursor.fetchone()[0]
            
            # 최근 수집 시간
            cursor.execute("SELECT MAX(collected_at) FROM ranking_history")
            latest_collection = cursor.fetchone()[0]
            
            # 총 수집 횟수
            cursor.execute("SELECT COUNT(DISTINCT collected_at) FROM ranking_history")
            total_collections = cursor.fetchone()[0]
            
            return HealthStatus(
                status="healthy",
                database_connected=True,
                total_products=total_products,
                total_brands=total_brands,
                latest_collection=format_datetime(latest_collection),
                total_collections=total_collections,
                api_version="2.0.0"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/api/products/current", response_model=List[Product], tags=["Products"])
async def get_current_products(
    limit: int = Query(200, ge=1, le=200, description="조회할 제품 수"),
    brand: Optional[str] = Query(None, description="브랜드명 필터"),
    category: Optional[str] = Query(None, description="카테고리 필터")
):
    """현재 최신 순위의 제품 목록 조회"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 최신 수집 시간 조회
            cursor.execute("SELECT MAX(collected_at) FROM ranking_history")
            latest_time = cursor.fetchone()[0]
            
            if not latest_time:
                return []
            
            # 제품 목록 조회
            query = """
                SELECT 
                    p.product_id,
                    p.brand_name,
                    p.product_name,
                    rh.sale_price as price,
                    rh.discount_rate,
                    p.image_url,
                    rh.ranking,
                    rh.collected_at
                FROM products p
                JOIN ranking_history rh ON p.product_id = rh.product_id
                WHERE rh.collected_at = ?
            """
            params = [latest_time]
            
            if brand:
                query += " AND p.brand_name = ?"
                params.append(brand)
            
            if category:
                query += " AND p.category_key = ?"
                params.append(category)
            
            query += " ORDER BY rh.ranking ASC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            products = []
            for row in rows:
                products.append(Product(
                    product_id=row['product_id'],
                    brand_name=row['brand_name'],
                    product_name=row['product_name'],
                    price=row['price'],
                    discount_rate=row['discount_rate'],
                    image_url=row['image_url'],
                    ranking=row['ranking'],
                    collected_at=format_datetime(row['collected_at'])
                ))
            
            return products
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch products: {str(e)}")


@app.get("/api/brands/list", response_model=List[str], tags=["Brands"])
async def get_all_brands():
    """모든 브랜드 목록 조회"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT brand_name 
                FROM products 
                WHERE brand_name IS NOT NULL AND brand_name != 'N/A'
                ORDER BY brand_name
            """)
            
            rows = cursor.fetchall()
            return [row['brand_name'] for row in rows]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch brand list: {str(e)}")


@app.get("/api/brands/stats", response_model=List[BrandStats], tags=["Brands"])
async def get_brand_statistics(
    sort_by: str = Query("product_count", enum=["product_count", "total_value", "avg_price"]),
    limit: int = Query(50, ge=1, le=200, description="조회할 브랜드 수")
):
    """브랜드별 통계 조회"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 최신 수집 시간
            cursor.execute("SELECT MAX(collected_at) FROM brand_stats_history")
            latest_time = cursor.fetchone()[0]
            
            if not latest_time:
                return []
            
            # 정렬 기준 매핑
            sort_column_map = {
                "product_count": "product_count DESC",
                "total_value": "(avg_price * product_count) DESC",
                "avg_price": "avg_price DESC"
            }
            sort_clause = sort_column_map.get(sort_by, "product_count DESC")
            
            query = f"""
                SELECT 
                    brand_name,
                    product_count,
                    (avg_price * product_count) as total_value,
                    avg_price,
                    avg_discount_rate,
                    avg_ranking as min_ranking,
                    avg_ranking as max_ranking,
                    collected_at as last_updated
                FROM brand_stats_history
                WHERE collected_at = ?
                ORDER BY {sort_clause}
                LIMIT ?
            """
            
            cursor.execute(query, [latest_time, limit])
            rows = cursor.fetchall()
            
            stats = []
            for row in rows:
                stats.append(BrandStats(
                    brand_name=row['brand_name'],
                    product_count=row['product_count'],
                    total_value=int(row['total_value']) if row['total_value'] else 0,
                    avg_price=row['avg_price'],
                    avg_discount_rate=row['avg_discount_rate'],
                    min_ranking=int(row['min_ranking']) if row['min_ranking'] else 0,
                    max_ranking=int(row['max_ranking']) if row['max_ranking'] else 0,
                    last_updated=format_datetime(row['last_updated'])
                ))
            
            return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch brand stats: {str(e)}")


@app.get("/api/products/{product_id}/history", response_model=List[ProductHistory], tags=["Products"])
async def get_product_history(
    product_id: str,
    days: int = Query(7, ge=1, le=30, description="조회할 일수")
):
    """특정 제품의 히스토리 조회"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 제품 존재 확인
            cursor.execute("SELECT product_id FROM products WHERE product_id = ?", [product_id])
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
            
            # 히스토리 조회
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            query = """
                SELECT 
                    collected_at,
                    ranking,
                    sale_price as price,
                    discount_rate
                FROM ranking_history
                WHERE product_id = ? AND collected_at >= ?
                ORDER BY collected_at DESC
            """
            
            cursor.execute(query, [product_id, since_date])
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                history.append(ProductHistory(
                    collected_at=format_datetime(row['collected_at']),
                    ranking=row['ranking'],
                    price=row['price'],
                    discount_rate=row['discount_rate']
                ))
            
            return history
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch product history: {str(e)}")


@app.get("/api/price-changes", response_model=List[PriceChange], tags=["Changes"])
async def get_price_changes(
    days: int = Query(7, ge=1, le=30, description="조회할 일수"),
    limit: int = Query(50, ge=1, le=200, description="조회할 변동 수")
):
    """가격 변동 이력 조회"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            query = """
                SELECT 
                    pc.product_id,
                    p.brand_name,
                    p.product_name,
                    pc.previous_sale_price as old_price,
                    pc.current_sale_price as new_price,
                    pc.price_change_amount as price_diff,
                    pc.price_change_percentage as price_diff_percent,
                    pc.changed_at
                FROM price_changes pc
                JOIN products p ON pc.product_id = p.product_id
                WHERE pc.changed_at >= ?
                ORDER BY pc.changed_at DESC
                LIMIT ?
            """
            
            cursor.execute(query, [since_date, limit])
            rows = cursor.fetchall()
            
            changes = []
            for row in rows:
                changes.append(PriceChange(
                    product_id=row['product_id'],
                    brand_name=row['brand_name'],
                    product_name=row['product_name'],
                    old_price=row['old_price'],
                    new_price=row['new_price'],
                    price_diff=row['price_diff'],
                    price_diff_percent=row['price_diff_percent'],
                    changed_at=format_datetime(row['changed_at'])
                ))
            
            return changes
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch price changes: {str(e)}")


@app.get("/api/ranking-changes", response_model=List[RankingChange], tags=["Changes"])
async def get_ranking_changes(
    days: int = Query(7, ge=1, le=30, description="조회할 일수"),
    change_type: Optional[str] = Query(None, enum=["상승", "하락"], description="변동 유형"),
    limit: int = Query(50, ge=1, le=200, description="조회할 변동 수")
):
    """순위 변동 이력 조회"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            query = """
                SELECT 
                    rc.product_id,
                    p.brand_name,
                    p.product_name,
                    rc.previous_ranking as old_ranking,
                    rc.current_ranking as new_ranking,
                    rc.change_amount as ranking_diff,
                    rc.change_type,
                    rc.changed_at
                FROM ranking_changes rc
                JOIN products p ON rc.product_id = p.product_id
                WHERE rc.changed_at >= ?
            """
            params = [since_date]
            
            if change_type:
                query += " AND rc.change_type = ?"
                params.append(change_type)
            
            query += " ORDER BY rc.changed_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            changes = []
            for row in rows:
                changes.append(RankingChange(
                    product_id=row['product_id'],
                    brand_name=row['brand_name'],
                    product_name=row['product_name'],
                    old_ranking=row['old_ranking'],
                    new_ranking=row['new_ranking'],
                    ranking_diff=row['ranking_diff'],
                    change_type=row['change_type'],
                    changed_at=format_datetime(row['changed_at'])
                ))
            
            return changes
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ranking changes: {str(e)}")


@app.get("/api/jobs/history", response_model=List[ScrapingJob], tags=["Jobs"])
async def get_scraping_jobs(
    limit: int = Query(20, ge=1, le=100, description="조회할 작업 수")
):
    """스크래핑 작업 이력 조회"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    id as job_id,
                    started_at,
                    completed_at,
                    status,
                    products_collected,
                    error_message,
                    execution_time_seconds as duration_seconds
                FROM scraping_logs
                ORDER BY started_at DESC
                LIMIT ?
            """
            
            cursor.execute(query, [limit])
            rows = cursor.fetchall()
            
            jobs = []
            for row in rows:
                jobs.append(ScrapingJob(
                    job_id=row['job_id'],
                    started_at=format_datetime(row['started_at']),
                    completed_at=format_datetime(row['completed_at']),
                    status=row['status'],
                    products_collected=row['products_collected'],
                    error_message=row['error_message'],
                    duration_seconds=row['duration_seconds']
                ))
            
            return jobs
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch job history: {str(e)}")


@app.get("/api/trends/brand/{brand_name}", tags=["Trends"])
async def get_brand_ranking_trend(
    brand_name: str,
    days: int = Query(7, ge=1, le=30, description="조회할 일수")
):
    """브랜드의 순위 동향 조회"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            query = """
                SELECT 
                    bsh.collected_at,
                    bsh.product_count,
                    bsh.avg_ranking,
                    bsh.avg_price,
                    bsh.avg_discount_rate
                FROM brand_stats_history bsh
                WHERE bsh.brand_name = ?
                AND bsh.collected_at >= ?
                ORDER BY bsh.collected_at ASC
            """
            
            cursor.execute(query, [brand_name, since_date])
            rows = cursor.fetchall()
            
            trend_data = []
            for row in rows:
                trend_data.append({
                    'collected_at': format_datetime(row['collected_at']),
                    'product_count': row['product_count'],
                    'avg_ranking': row['avg_ranking'],
                    'avg_price': row['avg_price'],
                    'avg_discount_rate': row['avg_discount_rate']
                })
            
            return {
                'brand_name': brand_name,
                'period_days': days,
                'data': trend_data
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch brand trend: {str(e)}")


@app.get("/api/trends/product/{product_id}", tags=["Trends"])
async def get_product_ranking_trend(
    product_id: str,
    days: int = Query(7, ge=1, le=30, description="조회할 일수")
):
    """특정 제품의 순위 동향 조회"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 제품 정보 조회
            cursor.execute("""
                SELECT product_name, brand_name 
                FROM products 
                WHERE product_id = ?
            """, [product_id])
            
            product_info = cursor.fetchone()
            if not product_info:
                raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
            
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            query = """
                SELECT 
                    rh.collected_at,
                    rh.ranking,
                    rh.sale_price,
                    rh.discount_rate
                FROM ranking_history rh
                WHERE rh.product_id = ?
                AND rh.collected_at >= ?
                ORDER BY rh.collected_at ASC
            """
            
            cursor.execute(query, [product_id, since_date])
            rows = cursor.fetchall()
            
            trend_data = []
            for row in rows:
                trend_data.append({
                    'collected_at': format_datetime(row['collected_at']),
                    'ranking': row['ranking'],
                    'price': row['sale_price'],
                    'discount_rate': row['discount_rate']
                })
            
            return {
                'product_id': product_id,
                'product_name': product_info['product_name'],
                'brand_name': product_info['brand_name'],
                'period_days': days,
                'data': trend_data
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch product trend: {str(e)}")


# ==================== Error Handlers ====================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "detail": "The requested resource was not found",
        "path": str(request.url)
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "error": "Internal Server Error",
        "detail": "An unexpected error occurred",
        "path": str(request.url)
    }


# ==================== Startup/Shutdown Events ====================

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행"""
    print("=" * 50)
    print("🚀 W Concept Tracking API Server Starting...")
    print("=" * 50)
    print(f"📚 API Documentation: http://localhost:8000/api/docs")
    print(f"📖 ReDoc: http://localhost:8000/api/redoc")
    print(f"💾 Database: {DB_PATH}")
    print("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 실행"""
    print("\n🛑 W Concept Tracking API Server Shutting Down...")


# ==================== Main ====================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 60)
    print("🚀 W Concept Best Products Tracking API Server")
    print("=" * 60)
    print("📍 Starting server on http://0.0.0.0:8000")
    print("📚 API Docs: http://localhost:8000/api/docs")
    print("📖 ReDoc: http://localhost:8000/api/redoc")
    print("=" * 60 + "\n")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 개발 모드: 코드 변경 시 자동 재시작
        log_level="info"
    )
