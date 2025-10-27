#!/bin/bash

# Fly.io 배포용 시작 스크립트
# API 서버 + 자동 크롤링 스케줄러 실행 (Option G)

echo "🚀 Starting W Concept Tracker Backend (with scheduler)..."

# 데이터베이스 경로 설정 (Volume 사용 시)
export DB_PATH="${DB_PATH:-./wconcept_tracking.db}"
echo "📁 Using database at: $DB_PATH"

# Volume 디렉토리 생성 (존재하지 않으면)
mkdir -p "$(dirname "$DB_PATH")"

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

# 크롤링 스케줄러 백그라운드 실행 (Option G)
echo "⏰ Starting crawling scheduler..."
python3 scheduler.py > /tmp/scheduler.log 2>&1 &
SCHEDULER_PID=$!
echo "✅ Scheduler started (PID: $SCHEDULER_PID, runs every hour at :20)"
echo "📝 Scheduler logs: /tmp/scheduler.log"

# API 서버 실행 (읽기+쓰기 모드, DB는 Fly.io 로컬에 직접 저장)
echo "🌐 Starting API server..."
echo "📝 Note: Crawling runs directly on Fly.io (every hour at :20 KST)"
echo "📝 No GitHub Actions delays, no redeployment needed!"

uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}
