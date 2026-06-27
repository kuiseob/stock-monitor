@echo off
REM Stock Monitor - 가장 간단한 실행 배치 파일
chcp 65001 > nul
cls

echo ════════════════════════════════════════════════════════
echo   📊 Stock Monitor - 실시간 주식 모니터링
echo ════════════════════════════════════════════════════════
echo.

REM 현재 디렉토리로 이동
cd /d "%~dp0"

echo ✅ 앱 시작 중...
echo 📍 접속: http://localhost:8501
echo.
echo 💡 첫 실행 시 10~20초 소요됩니다
echo.
echo ════════════════════════════════════════════════════════
echo.

REM 의존성 설치
echo 📦 라이브러리 확인 중...
python -m pip install -q -r requirements.txt >nul 2>&1

REM Streamlit 실행
python -m streamlit run streamlit/app.py

pause
