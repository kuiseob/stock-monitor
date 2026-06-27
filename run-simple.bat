@echo off
REM Stock Monitor - Windows 원클릭 실행 스크립트
REM UTF-8 인코딩 설정
chcp 65001 > nul
setlocal enabledelayedexpansion

cls
echo ════════════════════════════════════════════════════════
echo   📊 Stock Monitor - 실시간 주식 모니터링 대시보드
echo ════════════════════════════════════════════════════════
echo.

REM 현재 디렉토리 설정
set "SCRIPT_DIR=%~dp0"
cd /d "!SCRIPT_DIR!"

REM Python 경로 자동 감지
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_PATH=%%i"

REM Python 확인
if "!PYTHON_PATH!"=="" (
    echo ❌ Python을 찾을 수 없습니다.
    echo.
    echo 해결 방법:
    echo 1. Python 3.9 이상 설치
    echo 2. https://www.python.org 에서 다운로드
    echo 3. 설치 시 "Add Python to PATH" 필수!
    echo.
    pause
    exit /b 1
)

echo ✅ Python 확인됨: !PYTHON_PATH!
echo.

REM requirements.txt 확인
if not exist requirements.txt (
    echo ❌ requirements.txt 파일을 찾을 수 없습니다.
    echo.
    echo 이 배치 파일은 stock-monitor 폴더에 있어야 합니다.
    pause
    exit /b 1
)

echo 📦 필수 라이브러리 설치 중...
echo.

REM pip 업그레이드
"!PYTHON_PATH!" -m pip install --upgrade pip --quiet

REM 의존성 설치
"!PYTHON_PATH!" -m pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo ❌ 라이브러리 설치 실패
    echo.
    echo 다시 시도해주세요.
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

REM Streamlit 실행
"!PYTHON_PATH!" -m streamlit run streamlit/app.py

pause
