@echo off
REM Stock Monitor - Windows EXE 빌드 스크립트
REM 이 파일을 실행하면 독립 실행형 EXE 파일을 만듭니다

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   Stock Monitor - Windows EXE 빌더
echo ============================================
echo.

REM 현재 디렉토리
cd /d "%~dp0"

REM Python 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python이 설치되어 있지 않습니다.
    echo.
    echo Python 3.9 이상을 다음에서 다운로드하세요:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM 가상환경 확인
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] 가상환경을 생성 중입니다...
    python -m venv venv
)

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM PyInstaller 설치
echo [INFO] PyInstaller를 확인 중입니다...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller를 설치 중입니다...
    pip install -q pyinstaller
)

REM 의존성 설치
echo [INFO] 필요한 패키지를 설치 중입니다...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] 패키지 설치 실패
    pause
    exit /b 1
)

REM 빌드 시작
echo.
echo [INFO] Windows EXE 파일을 생성 중입니다...
echo (이 과정은 2-5분 정도 소요됩니다)
echo.

REM PyInstaller 실행
python build_windows_exe.py
if errorlevel 1 (
    echo [ERROR] EXE 빌드 실패
    pause
    exit /b 1
)

echo.
echo ============================================
echo   빌드 완료!
echo ============================================
echo.
echo dist\StockMonitor.exe 파일이 생성되었습니다.
echo.
echo 사용 방법:
echo   1. dist\StockMonitor.exe를 더블클릭해서 실행
echo   2. 또는 dist 폴더 전체를 다른 PC에 복사해서 사용
echo.
echo 주의사항:
echo   - 첫 실행 시 로딩이 오래 걸릴 수 있습니다 (1-2분)
echo   - Python이 설치되지 않은 PC에서도 실행 가능합니다
echo   - .env 파일을 편집해서 API 키를 입력하세요
echo.

pause
