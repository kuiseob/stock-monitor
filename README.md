# 삼성증권 API 기반 실시간 주식 모니터링 대시보드

5개 종목의 **실시간 외국인/기관 매매 현황**을 모니터링하는 Streamlit 웹 대시보드입니다.

## 주요 기능

✨ **실시간 데이터 수집**
- 삼성증권 Atosplus WebSocket API를 통한 1초 단위 데이터 수집
- 5개 종목의 실시간 주가 및 거래량 추적
- 외국인/기관 투자자 순매수/순매도 현황

📊 **시각화 대시보드**
- 실시간 가격 및 누적 거래량 표시
- 시간별, 일별 차트 및 통계
- 과거 데이터 조회 및 CSV 다운로드

🔔 **알림 기능**
- 특정 거래량 초과 시 알림
- 순매수 반전 감지

🛡️ **안정성**
- 자동 재연결 (지수 백오프)
- SQLite 기반 데이터 저장소
- 로깅 및 모니터링

## 필수 요구사항

- Python 3.9+
- 삼성증권 계좌 (API 키 발급 필요)

## 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd stock-monitor

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일에서 다음 정보 입력:
# - SAMSUNG_API_KEY
# - SAMSUNG_ACCOUNT_ID
# - SAMSUNG_API_SECRET
```

### 3. 앱 실행

```bash
# Streamlit 서버 시작
streamlit run streamlit/app.py

# 브라우저에서 http://localhost:8501 접속
```

## 프로젝트 구조

```
stock-monitor/
├── config/                    # 설정 파일
│   ├── stocks.json           # 모니터링 종목 설정
│   └── settings.json         # API 엔드포인트, 정책
├── data/                      # 데이터 저장소
│   └── stock_data.db         # SQLite 데이터베이스
├── src/                       # Python 패키지
│   ├── api/                  # API 통합
│   │   ├── atosplus_client.py      # WebSocket 클라이언트
│   │   ├── websocket_manager.py    # 연결 관리
│   │   └── models.py               # 데이터 모델
│   ├── database/             # 데이터베이스
│   │   ├── manager.py              # SQLite 관리자
│   │   └── queries.py              # 쿼리 헬퍼
│   ├── services/             # 비즈니스 로직
│   │   ├── stock_service.py        # 주식 서비스
│   │   └── cache_service.py        # 캐싱 서비스
│   └── utils/                # 유틸리티
│       ├── config.py               # 설정 로더
│       ├── logger.py               # 로깅
│       └── validators.py           # 검증
├── streamlit/                 # Streamlit 애플리케이션
│   ├── app.py                # 메인 앱
│   ├── pages/                # 페이지들
│   │   ├── 1_Overview.py     # 실시간 대시보드
│   │   ├── 2_Detailed_Analytics.py  # 차트 분석
│   │   ├── 3_History.py      # 과거 데이터
│   │   └── 4_Settings.py     # 환경설정
│   └── components/           # 재사용 가능한 컴포넌트
├── tests/                     # 단위 테스트
├── logs/                      # 로그 파일 (자동 생성)
├── requirements.txt           # Python 의존성
├── .env.example              # 환경변수 템플릿
├── .gitignore                # Git 제외 설정
└── README.md                 # 이 파일
```

## 설정

### config/stocks.json

모니터링할 종목을 정의합니다:

```json
{
  "stocks": [
    {"code": "005930", "name": "삼성전자", "market": "KOSPI"},
    {"code": "000660", "name": "SK하이닉스", "market": "KOSPI"}
  ],
  "update_interval_seconds": 1
}
```

### .env 파일

```bash
SAMSUNG_API_KEY=your_api_key_here
SAMSUNG_ACCOUNT_ID=your_account_id_here
SAMSUNG_API_SECRET=your_secret_key_here
ATOSPLUS_WS_URL=wss://api.atosplus.samsung.co.kr/websocket
DEFAULT_STOCKS=005930,000660,006400,051910,005380
DATABASE_PATH=./data/stock_data.db
RETENTION_DAYS=30
LOG_LEVEL=INFO
```

## 사용법

### 웹 대시보드

1. **Overview 페이지**: 5개 종목의 실시간 가격 및 거래량
2. **Analytics 페이지**: 시간별, 일별 차트 및 통계
3. **History 페이지**: 과거 데이터 조회 및 다운로드
4. **Settings 페이지**: API 자격증명 및 옵션 설정

### API 및 데이터베이스

Python 스크립트에서 직접 사용 가능:

```python
from src.database.manager import DatabaseManager
from src.api.atosplus_client import AtosplusClient

# 데이터베이스 조회
db = DatabaseManager()
prices = db.get_prices("005930", hours=24)

# API 연결
client = AtosplusClient(api_key, account_id, ws_url)
client.connect()
```

## 개발

### 테스트 실행

```bash
# 모든 테스트 실행
python3 -m unittest discover -s tests -p "test_*.py" -v

# 특정 테스트 실행
python3 -m unittest tests.test_database -v
```

### 코드 스타일

- PEP 8 준수
- 타입 힌트 사용
- 핵심 함수는 docstring 작성

## 트러블슈팅

### WebSocket 연결 실패
- API 키 확인
- Atosplus 서버 상태 확인
- 방화벽/프록시 설정 확인

### 데이터 저장 오류
- 데이터 디렉토리 권한 확인
- 디스크 공간 확인

### Streamlit 성능 저하
- 브라우저 캐시 정리
- 데이터 보관 기간 확인

## 라이선스

MIT License

## 기여

피드백과 제안은 환영합니다!

## 지원

문제가 발생한 경우 logs/app.log 파일을 확인하세요.
