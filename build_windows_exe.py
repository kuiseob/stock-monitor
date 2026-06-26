#!/usr/bin/env python3
"""
Windows용 실행 파일 빌더
PyInstaller를 사용하여 Streamlit 앱을 Windows EXE로 변환합니다.

사용법:
    python build_windows_exe.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(text):
    """헤더 출력"""
    print("\n" + "="*50)
    print(f"  {text}")
    print("="*50 + "\n")

def run_command(cmd, description=""):
    """명령어 실행"""
    if description:
        print(f"[INFO] {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} 실패")
        print(e.stderr)
        return False

def main():
    print_header("Stock Monitor - Windows EXE 빌드")

    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)

    # 1. 필요한 도구 확인
    print("[1/6] 필요한 도구 확인 중...")

    # Python 버전 확인
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 9:
        print(f"[ERROR] Python 3.9 이상이 필요합니다. (현재: {python_version.major}.{python_version.minor})")
        return False

    print(f"✓ Python {python_version.major}.{python_version.minor}")

    # 2. PyInstaller 설치 확인
    print("\n[2/6] PyInstaller 설치 확인 중...")
    result = subprocess.run("pip show pyinstaller", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("[INFO] PyInstaller를 설치 중입니다...")
        if not run_command("pip install -q pyinstaller", "PyInstaller 설치"):
            return False
    print("✓ PyInstaller 준비됨")

    # 3. 의존성 설치
    print("\n[3/6] Python 의존성 설치 중...")
    if not run_command("pip install -q -r requirements.txt", "의존성 설치"):
        return False
    print("✓ 의존성 설치 완료")

    # 4. 빌드 디렉토리 정리
    print("\n[4/6] 빌드 디렉토리 정리 중...")
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ {dir_name}/ 디렉토리 삭제")

    # 5. EXE 빌드
    print("\n[5/6] Windows EXE 파일 생성 중...")
    print("(이 과정은 1-3분 정도 소요됩니다)\n")

    # PyInstaller 명령어
    pyinstaller_cmd = (
        "pyinstaller "
        "--name=StockMonitor "
        "--onefile "
        "--windowed "
        "--icon=stock-monitor.ico "
        "--add-data=\"streamlit:streamlit\" "
        "--add-data=\"config:config\" "
        "--add-data=\".env.example:.\" "
        "--hidden-import=streamlit "
        "--hidden-import=pandas "
        "--hidden-import=plotly "
        "streamlit/app.py"
    )

    if not run_command(pyinstaller_cmd, "EXE 생성"):
        print("\n[WARNING] PyInstaller로 EXE를 생성할 수 없었습니다.")
        print("대신 run.bat 파일을 사용하세요.")
        return False

    # 6. 최종 정리
    print("\n[6/6] 최종 정리 중...")

    # 실행 파일 확인
    exe_path = project_root / "dist" / "StockMonitor.exe"
    if exe_path.exists():
        print(f"✓ EXE 파일 생성 완료: {exe_path}")
        print(f"  파일 크기: {exe_path.stat().st_size / (1024*1024):.1f} MB")

        # 실행 가능 확인
        print("\n[SUCCESS] Windows EXE 빌드 완료!")
        print_header("다음 단계")
        print("1. dist/StockMonitor.exe를 실행하세요")
        print("2. 또는 dist 폴더 전체를 다른 PC에 복사해서 사용하세요")
        print("\n주의사항:")
        print("- Python이 설치되지 않은 PC에서도 실행 가능합니다")
        print("- 첫 실행 시 1-2분 정도 소요됩니다 (자동 로딩)")
        print("- .env 파일을 편집해서 API 키를 입력하세요")

        return True
    else:
        print("[ERROR] EXE 파일 생성 실패")
        return False

if __name__ == "__main__":
    print_header("Stock Monitor Windows EXE 빌더")
    success = main()

    if not success:
        print("\n" + "="*50)
        print("  빌드 실패")
        print("="*50)
        print("\n[해결 방법]")
        print("1. Python이 PATH에 설정되어 있는지 확인하세요")
        print("2. 관리자 권한으로 실행해보세요")
        print("3. 또는 run.bat 파일을 사용하세요")
        sys.exit(1)

    sys.exit(0)
