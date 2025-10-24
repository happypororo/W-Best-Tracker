#!/bin/bash

# Fly.io 배포용 시작 스크립트
# API 서버만 실행 (크롤링은 GitHub Actions에서 담당)

echo "🚀 Starting W Concept Tracker Backend..."

# 볼륨 디렉토리 확인 및 생성
if [ -d "/data" ]; then
    echo "📁 Using persistent volume at /data"
    export DB_PATH="/data/wconcept_tracking.db"
else
    echo "📁 Using local directory for database"
    export DB_PATH="./wconcept_tracking.db"
fi

# 데이터베이스 초기화
echo "📊 Initializing database at $DB_PATH..."
python3 -c "import os; from database import Database; db = Database(os.environ.get('DB_PATH', 'wconcept_tracking.db')); print('Database initialized')"

# API 서버만 실행 (스케줄러 제거)
echo "🌐 Starting API server (read-only mode)..."
echo "⚠️  Crawling is handled by GitHub Actions"
uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}
