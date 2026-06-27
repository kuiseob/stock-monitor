@echo off
chcp 65001 > nul
cls

echo ════════════════════════════════════════════════════════
echo   📊 Stock Monitor - 실시간 주식 모니터링 대시보드
echo ════════════════════════════════════════════════════════
echo.
echo ✅ 자동 설정 중...
echo.

REM 현재 디렉토리로 이동
cd /d "%~dp0"

REM Python 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python을 찾을 수 없습니다.
    echo.
    echo 해결 방법:
    echo 1. Python 3.9 이상 설치 필요
    echo 2. https://www.python.org에서 다운로드
    echo 3. 설치 시 "Add Python to PATH" 체크하기
    echo.
    pause
    exit /b 1
)

echo ✅ Python 확인됨
echo.

REM 의존성 설치
echo 📦 필수 라이브러리 설치 중...
echo.
pip install -q --upgrade pip
pip install -q -r requirements.txt

if errorlevel 1 (
    echo ❌ 라이브러리 설치 실패
    pause
    exit /b 1
)

echo.
echo ✅ 설치 완료!
echo.
echo 🚀 앱 시작 중...
echo.
echo 📍 접속 주소: http://localhost:8501
echo.
echo 💡 팁: 첫 실행 시 10~20초 소요됩니다
echo.
echo ════════════════════════════════════════════════════════
echo.

REM Streamlit 앱 실행
streamlit run streamlit/app.py

pause
