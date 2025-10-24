#!/bin/bash

# Fly.io 배포용 시작 스크립트
# API 서버 + 스케줄러 실행

echo "🚀 Starting W Concept Tracker Backend..."

# 데이터베이스 경로 설정
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

# 스케줄러 백그라운드 실행 (매시간 :20분)
echo "⏰ Starting scheduler (runs every hour at :20)..."
python3 scheduler.py &
SCHEDULER_PID=$!

# API 서버 실행
echo "🌐 Starting API server..."
uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000} &
API_PID=$!

# 프로세스 관리
trap "echo '🛑 Shutting down...'; kill $SCHEDULER_PID $API_PID; exit 0" SIGTERM SIGINT

echo "✅ Backend services started:"
echo "   - Scheduler (PID: $SCHEDULER_PID)"
echo "   - API Server (PID: $API_PID)"

# 두 프로세스 모두 종료될 때까지 대기
wait
