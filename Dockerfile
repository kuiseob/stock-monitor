FROM python:3.12-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# 디렉토리 생성
RUN mkdir -p data logs .streamlit

# Streamlit 설정 복사
COPY .streamlit/config.toml .streamlit/

# 포트 노출
EXPOSE 8501

# 헬스 체크
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 앱 실행
CMD ["streamlit", "run", "streamlit/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
