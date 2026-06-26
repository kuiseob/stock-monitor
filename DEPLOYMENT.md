# 배포 가이드

## 로컬 환경에서 실행

### 1. 개발 환경 설정 완료 확인

```bash
cd /Users/kuiseob/stock-monitor

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치 확인
pip list | grep streamlit
```

### 2. 환경변수 설정 확인

```bash
# .env 파일 확인
cat .env

# 다음 값들이 설정되어 있는지 확인:
# - SAMSUNG_API_KEY
# - SAMSUNG_ACCOUNT_ID
# - SAMSUNG_API_SECRET
```

### 3. 앱 실행

```bash
# Streamlit 앱 시작
streamlit run streamlit/app.py

# 또는 Makefile 사용
make run
```

### 4. 브라우저 접속

자동으로 열리지 않으면:
```
http://localhost:8501
```

## Docker를 사용한 배포

### 1. Dockerfile 생성

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# 디렉토리 생성
RUN mkdir -p data logs

# Streamlit 설정
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 포트 노출
EXPOSE 8501

# 앱 실행
CMD ["streamlit", "run", "streamlit/app.py"]
```

### 2. Docker 이미지 빌드

```bash
# 이미지 빌드
docker build -t stock-monitor:latest .

# 이미지 확인
docker images | grep stock-monitor
```

### 3. Docker 컨테이너 실행

```bash
# 기본 실행
docker run -p 8501:8501 \
  -e SAMSUNG_API_KEY=your_key \
  -e SAMSUNG_ACCOUNT_ID=your_id \
  -e SAMSUNG_API_SECRET=your_secret \
  -v stock_data:/app/data \
  stock-monitor:latest

# 또는 docker-compose 사용
docker-compose up
```

## Docker Compose 설정

### docker-compose.yml 생성

```yaml
version: '3.8'

services:
  stock-monitor:
    build: .
    ports:
      - "8501:8501"
    environment:
      SAMSUNG_API_KEY: ${SAMSUNG_API_KEY}
      SAMSUNG_ACCOUNT_ID: ${SAMSUNG_ACCOUNT_ID}
      SAMSUNG_API_SECRET: ${SAMSUNG_API_SECRET}
      DATABASE_PATH: /app/data/stock_data.db
      LOG_FILE: /app/logs/app.log
    volumes:
      - stock_data:/app/data
      - stock_logs:/app/logs
    restart: unless-stopped
    networks:
      - stock-network

volumes:
  stock_data:
  stock_logs:

networks:
  stock-network:
    driver: bridge
```

### Docker Compose로 실행

```bash
# .env 파일에서 환경변수 로드
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

## 클라우드 배포 (선택사항)

### Heroku 배포

```bash
# Heroku 로그인
heroku login

# 앱 생성
heroku create stock-monitor

# Procfile 생성
echo "web: streamlit run streamlit/app.py --server.port=\$PORT" > Procfile

# 환경변수 설정
heroku config:set SAMSUNG_API_KEY=your_key
heroku config:set SAMSUNG_ACCOUNT_ID=your_id
heroku config:set SAMSUNG_API_SECRET=your_secret

# 배포
git push heroku main

# 앱 열기
heroku open
```

### AWS 배포

1. EC2 인스턴스 생성 (Ubuntu 22.04)
2. SSH 접속 후:

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Python 3.12 설치
sudo apt install python3.12 python3.12-venv -y

# 프로젝트 클론
git clone <repository-url>
cd stock-monitor

# 가상환경 설정
python3.12 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# .env 파일 생성
nano .env
# API 키 입력

# Systemd 서비스 생성
sudo nano /etc/systemd/system/stock-monitor.service

# 다음 내용 입력:
[Unit]
Description=Stock Monitor Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/stock-monitor
Environment="PATH=/home/ubuntu/stock-monitor/venv/bin"
ExecStart=/home/ubuntu/stock-monitor/venv/bin/streamlit run streamlit/app.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target

# 서비스 시작
sudo systemctl enable stock-monitor
sudo systemctl start stock-monitor

# 상태 확인
sudo systemctl status stock-monitor
```

## 프로덕션 체크리스트

- [ ] API 키 설정 확인
- [ ] 데이터베이스 권한 확인
- [ ] 로그 파일 경로 생성
- [ ] 방화벽 포트 8501 허용
- [ ] SSL 인증서 설정 (프록시 필요)
- [ ] 백업 정책 수립
- [ ] 모니터링 설정
- [ ] 에러 알림 설정

## 모니터링

### 로그 확인

```bash
# 실시간 로그 확인
tail -f logs/app.log

# 특정 날짜 로그
grep "2026-06-27" logs/app.log

# 에러만 확인
grep "ERROR" logs/app.log
```

### 데이터베이스 상태 확인

```bash
# DB 파일 크기
du -h data/stock_data.db

# 테이블 크기
sqlite3 data/stock_data.db "SELECT name, SUM(pgsize) as size FROM dbstat GROUP BY name;"
```

## 트러블슈팅

### Streamlit 포트 충돌

```bash
# 포트 변경
streamlit run streamlit/app.py --server.port 8502
```

### 메모리 부족

```bash
# 오래된 데이터 정리
python3 -c "from src.database.manager import DatabaseManager; DatabaseManager().cleanup_old_data(7)"
```

### WebSocket 연결 실패

1. API 키 확인
2. 네트워크 연결 확인
3. 방화벽 설정 확인
4. 서버 상태 확인

## 성능 최적화

### 데이터베이스 최적화

```sql
-- DB 분석
ANALYZE;

-- 인덱스 리빌드
REINDEX;

-- WAL 모드 확인
PRAGMA journal_mode;
```

### 메모리 최적화

```python
# 캐시 크기 제한
st.cache_data.clear()
```

## 백업 및 복구

### 자동 백업 설정 (매일 자정)

```bash
# 백업 스크립트 생성
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/stock-monitor"
mkdir -p $BACKUP_DIR
cp /Users/kuiseob/stock-monitor/data/stock_data.db $BACKUP_DIR/stock_data_$(date +%Y%m%d).db
# 30일 이상 된 백업 삭제
find $BACKUP_DIR -mtime +30 -delete
EOF

chmod +x backup.sh

# Crontab에 추가
crontab -e
# 다음 줄 추가: 0 0 * * * /path/to/backup.sh
```

### 백업 복구

```bash
# 최신 백업에서 복구
cp /backups/stock-monitor/stock_data_*.db data/stock_data.db
```

## 유지보수

### 정기점검 (월간)

- [ ] API 연결 상태 확인
- [ ] DB 용량 확인
- [ ] 에러 로그 검토
- [ ] 업데이트 확인
- [ ] 성능 지표 분석

### 업그레이드

```bash
# 의존성 업그레이드
pip install --upgrade -r requirements.txt

# 코드 업그레이드
git pull origin main
systemctl restart stock-monitor
```

## 보안

### API 키 보호

- 절대 버전 관리 시스템에 커밋하지 않기
- 환경변수 또는 .env 파일 사용
- 정기적으로 API 키 갱신

### 네트워크 보안

- HTTPS 적용 (프록시 사용)
- 방화벽 설정
- IP 화이트리스트 설정 (선택사항)

## 지원

문제 발생 시:
1. logs/app.log 확인
2. 데이터베이스 상태 확인
3. API 연결 상태 확인
4. GitHub Issues 검색
