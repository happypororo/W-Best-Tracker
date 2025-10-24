#!/bin/bash

# Fly.io 배포용 시작 스크립트
# API 서버만 실행 (크롤링은 GitHub Actions에서 담당)

echo "🚀 Starting W Concept Tracker Backend..."

# 데이터베이스 경로 설정
export DB_PATH="./wconcept_tracking.db"
echo "📁 Using database at: $DB_PATH"

# 데이터베이스 파일 확인
if [ -f "$DB_PATH" ]; then
    echo "✅ Database file found"
    ls -lh "$DB_PATH"
    
    # DB 통계 출력
    python3 -c "
import sqlite3
conn = sqlite3.connect('$DB_PATH')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM products')
products = cursor.fetchone()[0]
cursor.execute('SELECT MAX(collected_at) FROM ranking_history')
latest = cursor.fetchone()[0]
print(f'📊 Products: {products}, Latest: {latest}')
conn.close()
" || echo "⚠️  Could not read DB stats"
else
    echo "⚠️  Database file not found, will create new one"
fi

# 데이터베이스 초기화 (테이블 생성만)
echo "📊 Initializing database..."
python3 -c "from database import Database; db = Database(); print('✅ Database initialized')"

# API 서버 실행 (읽기 전용 모드)
echo "🌐 Starting API server (read-only mode)..."
echo "📝 Note: Crawling is handled by GitHub Actions (every hour at :20)"

uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}
