.PHONY: help install test run clean lint format docs

help:
	@echo "📊 Stock Monitor - 사용 가능한 명령어"
	@echo ""
	@echo "개발 환경:"
	@echo "  make install       - 의존성 설치"
	@echo "  make venv          - 가상환경 생성"
	@echo ""
	@echo "실행:"
	@echo "  make run           - Streamlit 앱 실행"
	@echo "  make run-debug     - 디버그 모드로 실행"
	@echo ""
	@echo "테스트:"
	@echo "  make test          - 모든 테스트 실행"
	@echo "  make test-unit     - 단위 테스트만 실행"
	@echo ""
	@echo "코드 관리:"
	@echo "  make lint          - 코드 스타일 체크"
	@echo "  make format        - 코드 포맷팅"
	@echo "  make clean         - 임시 파일 삭제"
	@echo ""
	@echo "문서:"
	@echo "  make docs          - 문서 보기"

venv:
	python3 -m venv venv
	@echo "✓ 가상환경 생성 완료"
	@echo "  활성화: source venv/bin/activate"

install:
	pip install -q -r requirements.txt
	@echo "✓ 의존성 설치 완료"

run:
	streamlit run streamlit/app.py

run-debug:
	streamlit run streamlit/app.py --logger.level=debug

test:
	python3 -m unittest discover -s tests -p "test_*.py" -v

test-unit:
	python3 -m unittest discover -s tests -p "test_*.py" -v 2>&1 | grep -E "^test_|OK|FAILED"

lint:
	python3 -m pylint src/ streamlit/ --disable=all --enable=E,F 2>/dev/null || echo "pylint not installed"

format:
	python3 -m black src/ streamlit/ tests/ 2>/dev/null || echo "black not installed"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null
	@echo "✓ 임시 파일 정리 완료"

docs:
	@echo "📖 문서 보기:"
	@echo ""
	@echo "1. README: README.md"
	@echo "2. 초기 설정: SETUP.md"
	@echo "3. 계획: .claude/plans/"
	@echo ""
	@echo "📌 빠른 시작:"
	@echo "  1. make venv"
	@echo "  2. source venv/bin/activate"
	@echo "  3. make install"
	@echo "  4. cp .env.example .env"
	@echo "  5. (편집) .env 파일에서 API 키 입력"
	@echo "  6. make run"

db-init:
	python3 -c "from src.database.manager import DatabaseManager; db = DatabaseManager(); print('✓ 데이터베이스 초기화 완료')" || echo "✗ 초기화 실패"

db-cleanup:
	python3 -c "from src.database.manager import DatabaseManager; db = DatabaseManager(); db.cleanup_old_data(); print('✓ 오래된 데이터 정리 완료')" || echo "✗ 정리 실패"

log:
	@if [ -f logs/app.log ]; then \
		tail -f logs/app.log; \
	else \
		echo "❌ 로그 파일이 없습니다. 앱을 먼저 실행하세요."; \
	fi

.DEFAULT_GOAL := help
