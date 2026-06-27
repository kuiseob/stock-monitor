#!/usr/bin/env python3
"""
Stock Monitor - Windows/Mac 크로스플랫폼 실행 래퍼
Streamlit을 직접 임포트해서 안정적으로 실행
"""

import sys
import os
from pathlib import Path

def setup_environment():
    """환경 설정"""
    app_dir = Path(__file__).parent.absolute()
    os.chdir(app_dir)

    # Streamlit 캐시 디렉토리 설정
    cache_dir = app_dir / ".streamlit_cache"
    cache_dir.mkdir(exist_ok=True)
    os.environ["STREAMLIT_CACHE_DIR"] = str(cache_dir)

    # Streamlit 서버 설정
    os.environ["STREAMLIT_SERVER_PORT"] = "8501"
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "localhost"
    os.environ["STREAMLIT_LOGGER_LEVEL"] = "error"
    os.environ["STREAMLIT_CLIENT_SHOWRRORDETAILS"] = "false"

def main():
    """Stock Monitor 앱 실행"""

    try:
        setup_environment()

        print("="*60)
        print("  📊 Stock Monitor")
        print("  실시간 주식 모니터링 대시보드")
        print("="*60)
        print()

        # Streamlit 임포트 및 실행
        try:
            import streamlit.cli as stcli

            print("✅ Streamlit 준비 완료")
            print()
            print("📍 앱 실행 중...")
            print("🌐 접속: http://localhost:8501")
            print()
            print("💡 팁: 첫 실행 시 10~20초 소요됩니다")
            print()
            print("-"*60)
            print()

            # Streamlit CLI 인수 설정
            sys.argv = [
                "streamlit",
                "run",
                "streamlit/app.py",
                "--server.port=8501",
                "--logger.level=error",
                "--client.showErrorDetails=false",
                "--client.toolbarMode=minimal"
            ]

            # Streamlit 메인 실행
            stcli.main()

        except ImportError as e:
            print(f"❌ Streamlit 로드 실패: {e}")
            print()
            print("해결 방법:")
            print("1. 이 파일은 EXE 내부에서만 실행 가능합니다")
            print("2. 또는 run.bat을 사용하세요 (더 안정적)")
            print("3. 또는 직접 실행: python streamlit/app.py")
            sys.exit(1)

    except KeyboardInterrupt:
        print()
        print()
        print("⏹️ 앱이 종료되었습니다")
        sys.exit(0)

    except Exception as e:
        print()
        print(f"❌ 오류 발생: {type(e).__name__}: {e}")
        print()
        print("해결 방법:")
        print("1. Python 3.9 이상 설치 확인")
        print("2. .env 파일에서 API 키 설정 확인")
        print("3. run.bat을 사용해보세요")
        sys.exit(1)

if __name__ == "__main__":
    main()
