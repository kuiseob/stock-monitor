import os
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Config:
    """프로젝트 설정 클래스"""

    # API 설정
    SAMSUNG_API_KEY = os.getenv("SAMSUNG_API_KEY", "")
    SAMSUNG_ACCOUNT_ID = os.getenv("SAMSUNG_ACCOUNT_ID", "")
    SAMSUNG_API_SECRET = os.getenv("SAMSUNG_API_SECRET", "")
    ATOSPLUS_WS_URL = os.getenv("ATOSPLUS_WS_URL", "wss://api.atosplus.samsung.co.kr/websocket")

    # 기본 종목
    DEFAULT_STOCKS_STR = os.getenv("DEFAULT_STOCKS", "005930,000660,006400,051910,005380")
    DEFAULT_STOCKS = [s.strip() for s in DEFAULT_STOCKS_STR.split(",")]

    # 데이터베이스
    DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/stock_data.db")
    RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "30"))

    # 로깅
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "./logs/app.log")

    # 개발 설정
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    @classmethod
    def validate(cls) -> bool:
        """설정 검증"""
        if not cls.SAMSUNG_API_KEY:
            print("⚠️  경고: SAMSUNG_API_KEY가 설정되지 않았습니다.")
            return False
        return True

    @classmethod
    def load_stocks_config(cls) -> dict:
        """config/stocks.json 로드"""
        config_path = Path(__file__).parent.parent.parent / "config" / "stocks.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"stocks": [], "update_interval_seconds": 1}

    @classmethod
    def get_stock_names(cls) -> dict:
        """종목명 매핑 딕셔너리 반환"""
        config = cls.load_stocks_config()
        return {stock["code"]: stock["name"] for stock in config.get("stocks", [])}
