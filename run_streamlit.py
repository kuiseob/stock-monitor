#!/usr/bin/env python3
"""
Streamlit 앱 실행 래퍼
PyInstaller EXE에서 streamlit을 subprocess로 실행

이 방식으로 streamlit 모듈 로딩 문제를 우회합니다.
"""

import subprocess
import sys
import os
from pathlib import Path
import webbrowser
import time

def main():
    """Streamlit 앱을 subprocess로 실행"""

    try:
        # 현재 디렉토리 설정
        app_dir = Path(__file__).parent.absolute()
        os.chdir(app_dir)

        print("="*60)
        print("  Stock Monitor - 실시간 주식 모니터링 대시보드")
        print("="*60)
        print()
        print("📍 앱 실행 중...")
        print()

        # streamlit 앱 실행
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "streamlit/app.py",
            "--server.port=8501",
            "--logger.level=error",
            "--client.showErrorDetails=false"
        ]

        print(f"💻 명령어: {' '.join(cmd)}")
        print()

        # 브라우저 자동 열기 (약간의 지연 후)
        print("🌐 브라우저 열기: http://localhost:8501")
        print()

        def open_browser():
            """몇 초 후 브라우저 열기"""
            time.sleep(3)
            try:
                webbrowser.open("http://localhost:8501")
            except:
                pass

        # 백그라운드에서 브라우저 열기
        import threading
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

        # Streamlit 실행
        print("⏳ 앱 로딩 중... (약 10-15초 소요)")
        print()
        print("-"*60)
        print()

        result = subprocess.run(cmd)
        sys.exit(result.returncode)

    except Exception as e:
        print(f"❌ 오류: {e}")
        print()
        print("해결 방법:")
        print("1. Python이 설치되어 있는지 확인")
        print("2. requirements.txt를 설치했는지 확인: pip install -r requirements.txt")
        print("3. 대신 run.bat을 사용해보세요")
        sys.exit(1)

if __name__ == "__main__":
    main()
