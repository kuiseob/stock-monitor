# 초기 설정 가이드

## Step 1: 삼성증권 API 키 발급

### 1.1 삼성증권 계좌 준비
- 삼성증권 증권 계좌 필요
- HTS 또는 MTS 앱 설치

### 1.2 Atosplus API 신청
1. 삼성증권 홈페이지 → 개발자센터 또는 고객지원
2. Atosplus API 신청
3. API 키, 계정 ID, 시크릿 키 발급 대기

### 1.3 발급받은 정보
다음 정보를 기록하세요:
- `SAMSUNG_API_KEY`: API 키
- `SAMSUNG_ACCOUNT_ID`: 계좌 ID
- `SAMSUNG_API_SECRET`: API 시크릿 키
- `ATOSPLUS_WS_URL`: WebSocket URL (기본값: `wss://api.atosplus.samsung.co.kr/websocket`)

## Step 2: 개발 환경 설정

### 2.1 Python 설치 확인
```bash
python3 --version
# Python 3.9 이상 필요
```

### 2.2 가상환경 생성
```bash
cd /Users/kuiseob/stock-monitor

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows
```

### 2.3 의존성 설치
```bash
pip install -r requirements.txt
```

설치되는 주요 패키지:
- `streamlit`: 웹 프레임워크
- `pandas`: 데이터 처리
- `plotly`: 차트 시각화
- `websocket-client`: WebSocket 통신
- `python-dotenv`: 환경변수 관리

## Step 3: 환경변수 설정

### 3.1 .env 파일 생성
```bash
cp .env.example .env
```

### 3.2 .env 파일 편집
```bash
# 텍스트 에디터로 .env 열기
# macOS/Linux:
nano .env
# 또는
vim .env

# Windows:
notepad .env
```

### 3.3 필수 환경변수 입력
```bash
# 삼성증권 API 자격증명
SAMSUNG_API_KEY=your_actual_api_key
SAMSUNG_ACCOUNT_ID=your_actual_account_id
SAMSUNG_API_SECRET=your_actual_secret_key

# WebSocket URL (기본값 사용 가능)
ATOSPLUS_WS_URL=wss://api.atosplus.samsung.co.kr/websocket

# 모니터링 종목 (코드로 쉼표 구분)
DEFAULT_STOCKS=005930,000660,006400,051910,005380

# 데이터베이스 경로
DATABASE_PATH=./data/stock_data.db

# 데이터 보관 기간 (일)
RETENTION_DAYS=30

# 로깅 레벨
LOG_LEVEL=INFO
```

### 3.4 권한 설정 (macOS/Linux)
```bash
chmod 600 .env  # .env 파일 보안
```

## Step 4: 데이터베이스 초기화

데이터베이스는 앱 실행 시 자동으로 초기화되지만, 수동으로도 할 수 있습니다:

```bash
python3 -c "from src.database.manager import DatabaseManager; DatabaseManager().health_check()"
```

## Step 5: 테스트 실행

### 5.1 기본 테스트
```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

### 5.2 특정 테스트
```bash
python3 -m unittest tests.test_database.TestDatabaseManager.test_insert_price -v
```

예상 결과:
```
test_insert_price ... ok
OK
```

## Step 6: Streamlit 앱 실행

### 6.1 개발 모드 실행
```bash
streamlit run streamlit/app.py
```

### 6.2 브라우저 접속
자동으로 브라우저가 열리지 않으면:
```
http://localhost:8501
```

### 6.3 초기 로딩
첫 실행 시:
1. WebSocket 연결 수립 (2-3초 소요)
2. 데이터 수집 시작
3. 대시보드 표시

## Step 7: 종목 설정

### 7.1 config/stocks.json 수정
```json
{
  "stocks": [
    {"code": "005930", "name": "삼성전자", "market": "KOSPI"},
    {"code": "000660", "name": "SK하이닉스", "market": "KOSPI"},
    {"code": "006400", "name": "삼성SDI", "market": "KOSPI"},
    {"code": "051910", "name": "LG화학", "market": "KOSPI"},
    {"code": "005380", "name": "현대차", "market": "KOSPI"}
  ],
  "update_interval_seconds": 1,
  "max_retries": 5,
  "retry_delay_seconds": 1
}
```

### 7.2 종목 코드 변경
주식 종목 코드는 한국거래소 공식 코드 사용:
- 005930: 삼성전자
- 000660: SK하이닉스
- 006400: 삼성SDI
- 051910: LG화학
- 005380: 현대차

[한국거래소 종목검색](http://kind.krx.co.kr/corpgeneral/main.do)에서 확인

## Step 8: 로그 확인

### 8.1 실시간 로그 확인
```bash
tail -f logs/app.log
```

### 8.2 로그 레벨 변경
.env 파일에서:
```bash
LOG_LEVEL=DEBUG  # 더 자세한 로그
LOG_LEVEL=INFO   # 기본값
LOG_LEVEL=WARNING # 경고만
```

## 문제 해결

### WebSocket 연결 실패
```
ERROR: ConnectionError: [Errno 111] Connection refused
```
**해결방법:**
- API 키가 올바른지 확인
- Atosplus 서버 상태 확인
- 방화벽/프록시 설정 확인
- logs/app.log에서 상세 에러 확인

### 데이터베이스 오류
```
ERROR: no such table: stock_prices
```
**해결방법:**
- DATABASE_PATH가 올바른지 확인
- 데이터 디렉토리 권한 확인
- DB 파일 삭제 후 재시작

### Streamlit 포트 충돌
```
ERROR: Address already in use
```
**해결방법:**
- 다른 포트 사용: `streamlit run streamlit/app.py --logger.level=debug --server.port 8502`
- 또는 기존 프로세스 종료

### 느린 성능
**해결방법:**
- 브라우저 캐시 정리
- 보관 기간 단축: `RETENTION_DAYS=7`
- 시스템 리소스 확인

## Streamlit 설정 파일 (선택사항)

`.streamlit/config.toml` 생성:
```toml
[client]
showErrorDetails = true

[logger]
level = "info"

[server]
maxUploadSize = 10
enableXsrfProtection = true
```

## Docker를 사용한 실행 (고급)

```bash
# Dockerfile 빌드
docker build -t stock-monitor .

# 컨테이너 실행
docker run -p 8501:8501 \
  -e SAMSUNG_API_KEY=your_key \
  -e SAMSUNG_ACCOUNT_ID=your_id \
  -e SAMSUNG_API_SECRET=your_secret \
  stock-monitor
```

## 다음 단계

1. **대시보드 탐색**: Overview, Analytics, History 페이지 사용
2. **로그 모니터링**: logs/app.log에서 실시간 데이터 수집 상황 확인
3. **알림 설정**: Settings에서 알림 조건 구성
4. **데이터 분석**: History 페이지에서 CSV 다운로드 후 분석

## 제한사항

- 장시간 API 미사용 시 연결 자동 종료 가능 (대략 4-6시간)
- 장애 시 자동 재연결 (최대 5회)
- 30일 이상 데이터는 자동 삭제

## 문의 및 지원

- 로그 파일: `logs/app.log`
- API 문제: 삼성증권 개발자센터
- 앱 이슈: GitHub Issues
