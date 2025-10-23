#!/bin/bash

# Railway 배포용 시작 스크립트
# API 서버와 스케줄러를 동시에 실행합니다

echo "🚀 Starting W Concept Tracker Backend..."

# 데이터베이스 초기화
echo "📊 Initializing database..."
python3 -c "from database import Database; db = Database('wconcept_tracking.db'); print('Database initialized')"

# 스케줄러를 백그라운드에서 실행
echo "⏰ Starting scheduler..."
python3 scheduler.py &
SCHEDULER_PID=$!

# API 서버 실행
echo "🌐 Starting API server..."
uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000} &
API_PID=$!

# 종료 시그�� 처리
trap "echo '🛑 Shutting down...'; kill $SCHEDULER_PID $API_PID; exit 0" SIGTERM SIGINT

# 두 프로세스가 실행 중인지 확인
echo "✅ Backend services started:"
echo "   - API Server (PID: $API_PID)"
echo "   - Scheduler (PID: $SCHEDULER_PID)"

# 프로세스가 종료될 때까지 대기
wait
