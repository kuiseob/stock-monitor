from typing import Dict, List, Optional
from datetime import datetime
from functools import lru_cache

from src.database.manager import DatabaseManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Streamlit 캐싱은 Streamlit 앱 내에서만 사용
# 테스트나 일반 환경에서는 간단한 lru_cache 사용
try:
    import streamlit as st
    HAS_STREAMLIT = hasattr(st, 'cache_data')
except ImportError:
    HAS_STREAMLIT = False

class CacheService:
    """데이터 캐싱 서비스"""

    def __init__(self, db: DatabaseManager = None):
        self.db = db or DatabaseManager()

    @staticmethod
    def get_price_history_cached(code: str, hours: int = 24) -> List[Dict]:
        """가격 이력 조회 (캐싱 가능)"""
        db = DatabaseManager()
        return db.get_prices(code, hours=hours)

    @staticmethod
    def get_trade_history_cached(code: str, hours: int = 24) -> List[Dict]:
        """거래 이력 조회 (캐싱 가능)"""
        db = DatabaseManager()
        return db.get_trades(code, hours=hours)

    @staticmethod
    def get_latest_price_cached(code: str) -> Optional[Dict]:
        """최신 가격 조회 (캐싱 가능)"""
        db = DatabaseManager()
        return db.get_latest_price(code)

    @staticmethod
    def get_latest_trade_cached(code: str) -> Optional[Dict]:
        """최신 거래 조회 (캐싱 가능)"""
        db = DatabaseManager()
        return db.get_latest_trade(code)

    @staticmethod
    def get_daily_summary_cached(code: str, date: str) -> Optional[Dict]:
        """일일 요약 조회 (캐싱 가능)"""
        db = DatabaseManager()
        return db.get_daily_summary(code, date)

    @staticmethod
    def get_database_manager() -> DatabaseManager:
        """DB 관리자 조회"""
        return DatabaseManager()

    @staticmethod
    def clear_all_cache():
        """모든 캐시 초기화"""
        logger.info("Cache clear requested")


class DataService:
    """데이터 처리 서비스 (캐싱과 함께)"""

    def __init__(self):
        self.cache = CacheService()

    def get_stock_overview(self, code: str) -> Dict:
        """종목 개요 조회"""
        latest_price = self.cache.get_latest_price_cached(code)
        latest_trade = self.cache.get_latest_trade_cached(code)

        if not latest_price:
            return {
                "code": code,
                "status": "no_data",
                "message": "아직 데이터가 수집되지 않았습니다."
            }

        price_range = self._get_price_range_cached(code)
        volatility = self._get_volatility_cached(code)

        return {
            "code": code,
            "current_price": latest_price.get("price"),
            "volume": latest_price.get("volume"),
            "bid": latest_price.get("bid"),
            "ask": latest_price.get("ask"),
            "min_price": price_range["min"],
            "max_price": price_range["max"],
            "volatility": volatility,
            "foreign_net": latest_trade.get("net_foreign") if latest_trade else 0,
            "institution_net": latest_trade.get("net_institution") if latest_trade else 0,
            "timestamp": latest_price.get("timestamp"),
        }

    def get_market_analytics(self, code: str, hours: int = 24) -> Dict:
        """시장 분석 데이터"""
        prices = self.cache.get_price_history_cached(code, hours=hours)
        trades = self.cache.get_trade_history_cached(code, hours=hours)

        if not prices or not trades:
            return {
                "code": code,
                "status": "insufficient_data",
                "message": "분석에 필요한 데이터가 부족합니다."
            }

        return {
            "code": code,
            "period_hours": hours,
            "price_data_points": len(prices),
            "trade_data_points": len(trades),
            "avg_price": sum(p["price"] for p in prices) / len(prices),
            "avg_volume": sum(p.get("volume", 0) for p in prices) / len(prices),
            "total_foreign_buy": sum(t.get("foreign_buy_volume", 0) for t in trades),
            "total_foreign_sell": sum(t.get("foreign_sell_volume", 0) for t in trades),
            "total_institution_buy": sum(t.get("institution_buy_volume", 0) for t in trades),
            "total_institution_sell": sum(t.get("institution_sell_volume", 0) for t in trades),
        }

    @staticmethod
    def _get_price_range_cached(code: str) -> Dict[str, Optional[float]]:
        """가격 범위 조회"""
        db = DatabaseManager()
        prices = db.get_prices(code, hours=24)

        if not prices:
            return {"min": None, "max": None}

        price_list = [p["price"] for p in prices]
        return {"min": min(price_list), "max": max(price_list)}

    @staticmethod
    def _get_volatility_cached(code: str) -> Optional[float]:
        """변동성 조회"""
        db = DatabaseManager()
        prices = db.get_prices(code, hours=24)

        if len(prices) < 2:
            return None

        price_list = [p["price"] for p in prices]
        import statistics
        return statistics.stdev(price_list)

    def format_price(self, price: float) -> str:
        """가격 포맷팅"""
        return f"{price:,.0f} 원"

    def format_volume(self, volume: int) -> str:
        """거래량 포맷팅"""
        if volume >= 1_000_000:
            return f"{volume / 1_000_000:.1f}M"
        elif volume >= 1_000:
            return f"{volume / 1_000:.1f}K"
        else:
            return str(volume)

    def format_percent(self, value: float) -> str:
        """백분율 포맷팅"""
        sign = "+" if value > 0 else ""
        return f"{sign}{value:.2f}%"
