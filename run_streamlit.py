#!/usr/bin/env python3
"""
Stock Monitor - 안정적 Windows/Mac 실행 래퍼
직접 streamlit run 명령어로 실행 (Subprocess 안정성)
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Stock Monitor 앱 실행"""

    try:
        # 현재 디렉토리 설정
        app_dir = Path(__file__).parent.absolute()
        os.chdir(app_dir)

        # 환경 변수 설정
        env = os.environ.copy()
        env["STREAMLIT_SERVER_PORT"] = "8501"
        env["STREAMLIT_SERVER_ADDRESS"] = "localhost"
        env["STREAMLIT_LOGGER_LEVEL"] = "error"
        env["STREAMLIT_CLIENT_SHOWRRORDETAILS"] = "false"

        print("="*60)
        print("  📊 Stock Monitor")
        print("  실시간 주식 모니터링 대시보드")
        print("="*60)
        print()
        print("✅ 앱 시작 중...")
        print("🌐 접속: http://localhost:8501")
        print()
        print("💡 첫 실행 시 10~20초 소요됩니다")
        print()
        print("-"*60)
        print()

        # Streamlit 실행
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

        # 프로세스 실행
        result = subprocess.run(cmd, env=env)
        sys.exit(result.returncode)

    except FileNotFoundError:
        print()
        print("❌ 오류: streamlit을 찾을 수 없습니다")
        print()
        print("해결 방법:")
        print("1. Python이 PATH에 등록되어 있는지 확인")
        print("2. 또는 run.bat을 사용하세요")
        sys.exit(1)

    except KeyboardInterrupt:
        print()
        print("⏹️ 앱이 종료되었습니다")
        sys.exit(0)

    except Exception as e:
        print()
        print(f"❌ 오류: {type(e).__name__}: {e}")
        print()
        print("해결 방법:")
        print("1. Python 3.9 이상 확인")
        print("2. requirements.txt 설치 확인")
        print("3. run.bat 사용")
        sys.exit(1)

if __name__ == "__main__":
    main()
