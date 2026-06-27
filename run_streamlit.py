#!/usr/bin/env python3
"""
Streamlit 앱 실행 래퍼 (개선된 버전)
직접 streamlit을 임포트해서 실행 (subprocess 문제 해결)
"""

import sys
import os
from pathlib import Path

def main():
    """Streamlit 앱을 직접 실행"""

    try:
        # 현재 디렉토리 설정
        app_dir = Path(__file__).parent.absolute()
        os.chdir(app_dir)

        print("="*60)
        print("  Stock Monitor")
        print("  실시간 주식 모니터링 대시보드")
        print("="*60)
        print()

        # Streamlit 직접 임포트 및 실행
        try:
            import streamlit.cli as stcli

            print("✅ Streamlit 로드 성공")
            print()
            print("📍 앱 실행 중...")
            print("🌐 브라우저: http://localhost:8501")
            print()
            print("-"*60)
            print()

            # Streamlit 실행
            sys.argv = [
                "streamlit",
                "run",
                "streamlit/app.py",
                "--server.port=8501",
                "--logger.level=error",
                "--client.showErrorDetails=false"
            ]

            stcli.main()

        except ImportError as e:
            print(f"❌ Streamlit 임포트 실패: {e}")
            print()
            print("대안: run.bat을 사용하세요")
            print("  run.bat는 Python 인터프리터를 직접 사용하여 더 안정적입니다")
            sys.exit(1)

    except KeyboardInterrupt:
        print()
        print("⏹️ 앱이 종료되었습니다")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print()
        print("해결 방법:")
        print("1. Python 3.9+ 설치 확인")
        print("2. requirements.txt 설치: pip install -r requirements.txt")
        print("3. run.bat 사용 권장")
        sys.exit(1)

if __name__ == "__main__":
    main()
