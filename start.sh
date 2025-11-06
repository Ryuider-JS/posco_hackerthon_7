#!/bin/bash

echo "========================================"
echo "Q-ProcureAssistant 시작"
echo "========================================"
echo ""

echo "[1/2] 백엔드 서버 시작 중..."
cd backend
gnome-terminal --title="Backend - FastAPI" -- bash -c "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; exec bash" 2>/dev/null || \
xterm -T "Backend - FastAPI" -e "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd \"'"$(pwd)"'\" && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"' 2>/dev/null || \
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
echo "✓ 백엔드 서버 실행됨 (http://localhost:8000)"
echo ""

sleep 3

echo "[2/2] 프론트엔드 서버 시작 중..."
cd ../frontend
gnome-terminal --title="Frontend - Vite" -- bash -c "npm run dev; exec bash" 2>/dev/null || \
xterm -T "Frontend - Vite" -e "npm run dev; bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd \"'"$(pwd)"'\" && npm run dev"' 2>/dev/null || \
npm run dev &
echo "✓ 프론트엔드 서버 실행됨 (http://localhost:5173)"
echo ""

echo "========================================"
echo "✅ 모든 서버가 실행되었습니다!"
echo "========================================"
echo ""
echo "- 백엔드 API: http://localhost:8000"
echo "- API 문서: http://localhost:8000/docs"
echo "- 프론트엔드: http://localhost:5173"
echo ""
echo "종료하려면 Ctrl+C를 누르세요."
echo ""

wait
