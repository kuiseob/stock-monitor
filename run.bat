@echo off
REM Stock Monitor - Windows 실행 스크립트
REM 이 파일을 더블클릭하면 애플리케이션이 실행됩니다

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   Stock Monitor - 실시간 주식 모니터링
echo ============================================
echo.

REM 현재 디렉토리 확인
cd /d "%~dp0"

REM Python 경로 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python이 설치되어 있지 않습니다.
    echo.
    echo 다음 링크에서 Python을 설치하세요:
    echo https://www.python.org/downloads/
    echo.
    echo 설치 시 "Add Python to PATH" 옵션을 반드시 체크하세요.
    echo.
    pause
    exit /b 1
)

REM 가상환경 확인
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] 가상환경을 생성 중입니다...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] 가상환경 생성 실패
        pause
        exit /b 1
    )
)

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM 의존성 설치
echo [INFO] 필요한 패키지를 설치 중입니다...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] 패키지 설치 실패
    pause
    exit /b 1
)

REM .env 파일 확인
if not exist ".env" (
    echo [WARNING] .env 파일이 없습니다.
    echo.
    echo .env.example을 복사 중입니다...
    copy ".env.example" ".env" >nul
    echo [INFO] .env 파일이 생성되었습니다.
    echo [WARNING] .env 파일을 편집해서 API 키를 입력하세요.
    echo.
)

REM 로그 디렉토리 생성
if not exist "logs" mkdir logs
if not exist "data" mkdir data

REM Streamlit 앱 실행
echo [INFO] 애플리케이션을 시작 중입니다...
echo.
echo 브라우저가 자동으로 열릴 것입니다.
echo 열리지 않으면 다음 주소를 브라우저에 입력하세요:
echo   http://localhost:8501
echo.
echo Ctrl+C를 누르면 애플리케이션이 종료됩니다.
echo.
timeout /t 2 /nobreak

streamlit run streamlit\app.py --server.port 8501

REM 가상환경 비활성화
deactivate

pause
