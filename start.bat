@echo off
chcp 65001 > nul
echo ========================================
echo Q-ProcureAssistant 시작
echo ========================================
echo.

echo [1/2] 백엔드 서버 시작 중...
cd backend
start "Backend - FastAPI" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ✓ 백엔드 서버 실행됨 (http://localhost:8000)
echo.

timeout /t 3 /nobreak > nul

echo [2/2] 프론트엔드 서버 시작 중...
cd ..\frontend
start "Frontend - Vite" cmd /k "npm run dev"
echo ✓ 프론트엔드 서버 실행됨 (http://localhost:5173)
echo.

echo ========================================
echo ✅ 모든 서버가 실행되었습니다!
echo ========================================
echo.
echo - 백엔드 API: http://localhost:8000
echo - API 문서: http://localhost:8000/docs
echo - 프론트엔드: http://localhost:5173
echo.
echo 종료하려면 각 창을 닫으세요.
echo.
pause
