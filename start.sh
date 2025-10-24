#!/bin/bash

# Fly.io 배포용 시작 스크립트
# API 서버만 실행 (크롤링은 GitHub Actions에서 담당)

echo "🚀 Starting W Concept Tracker Backend..."

# 데이터베이스 경로 설정 (Git에서 배포된 파일 사용)
export DB_PATH="./wconcept_tracking.db"
echo "📁 Using database at: $DB_PATH"

# 데이터베이스 파일 확인
if [ -f "$DB_PATH" ]; then
    echo "✅ Database file found"
    ls -lh "$DB_PATH"
else
    echo "⚠️  Database file not found, will create new one"
fi

# 데이터베이스 초기화
echo "📊 Initializing database..."
python3 -c "from database import Database; db = Database(); print('Database initialized')"

# API 서버만 실행 (스케줄러 제거)
echo "🌐 Starting API server (read-only mode)..."
echo "⚠️  Crawling is handled by GitHub Actions"
uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}
