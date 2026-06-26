import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from queue import Queue, Empty
import statistics

from src.api.atosplus_client import AtosplusClient
from src.api.models import StockPrice, ForexInstitutionalTrade
from src.database.manager import DatabaseManager
from src.utils.logger import setup_logger
from src.utils.config import Config

logger = setup_logger(__name__)

class StockService:
    """주식 데이터 수집 및 분석 서비스"""

    def __init__(self, api_key: str, account_id: str, api_secret: str):
        self.api_client = AtosplusClient(
            api_key=api_key,
            account_id=account_id,
            ws_url=Config.ATOSPLUS_WS_URL
        )
        self.db = DatabaseManager()
        self.running = False
        self.collector_thread = None
        self.saver_thread = None
        self.pending_prices = Queue()
        self.pending_trades = Queue()
        self.latest_data = {}

    def start(self, stock_codes: List[str]) -> bool:
        """서비스 시작"""
        if self.running:
            logger.warning("Service is already running")
            return False

        try:
            # API 클라이언트 콜백 등록
            self.api_client.on_price_update(self._on_price_received)
            self.api_client.on_trade_update(self._on_trade_received)
            self.api_client.on_error(self._on_api_error)

            # WebSocket 연결
            if not self.api_client.connect_with_retry():
                logger.error("Failed to connect to API")
                return False

            # 구독 시작
            self.api_client.subscribe_prices(stock_codes)
            self.api_client.subscribe_trades(stock_codes)

            # 백그라운드 스레드 시작
            self.running = True
            self.collector_thread = threading.Thread(
                target=self._collect_loop,
                args=(stock_codes,),
                daemon=True
            )
            self.saver_thread = threading.Thread(
                target=self._save_loop,
                daemon=True
            )

            self.collector_thread.start()
            self.saver_thread.start()

            logger.info(f"Service started with stocks: {stock_codes}")
            return True
        except Exception as e:
            logger.error(f"Error starting service: {e}")
            return False

    def stop(self) -> None:
        """서비스 중지"""
        self.running = False
        self.api_client.disconnect()
        logger.info("Service stopped")

    def _on_price_received(self, price: StockPrice) -> None:
        """가격 데이터 수신"""
        self.pending_prices.put(price)
        self.latest_data[f"price_{price.code}"] = price

    def _on_trade_received(self, trade: ForexInstitutionalTrade) -> None:
        """거래 데이터 수신"""
        self.pending_trades.put(trade)
        self.latest_data[f"trade_{trade.code}"] = trade

    def _on_api_error(self, error_msg: str) -> None:
        """API 에러 처리"""
        logger.error(f"API error: {error_msg}")

    def _collect_loop(self, stock_codes: List[str]) -> None:
        """수집 루프 (헬스체크)"""
        while self.running:
            try:
                if not self.api_client.health_check():
                    logger.warning("API health check failed, attempting reconnect")
                    if not self.api_client.connect_with_retry():
                        logger.error("Reconnection failed")
                    else:
                        self.api_client.subscribe_prices(stock_codes)
                        self.api_client.subscribe_trades(stock_codes)

                time.sleep(10)
            except Exception as e:
                logger.error(f"Error in collect loop: {e}")
                time.sleep(5)

    def _save_loop(self) -> None:
        """저장 루프 (데이터 일괄 저장)"""
        while self.running:
            try:
                # 가격 데이터 저장
                while not self.pending_prices.empty():
                    try:
                        price = self.pending_prices.get(timeout=0.1)
                        self.db.insert_price(price)
                    except Empty:
                        break

                # 거래 데이터 저장
                while not self.pending_trades.empty():
                    try:
                        trade = self.pending_trades.get(timeout=0.1)
                        self.db.insert_trade(trade)
                    except Empty:
                        break

                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in save loop: {e}")
                time.sleep(5)

    def get_latest_price(self, code: str) -> Optional[Dict]:
        """최신 가격 조회"""
        latest = self.db.get_latest_price(code)
        return latest

    def get_latest_trade(self, code: str) -> Optional[Dict]:
        """최신 거래 데이터 조회"""
        latest = self.db.get_latest_trade(code)
        return latest

    def get_price_history(self, code: str, hours: int = 24) -> List[Dict]:
        """가격 이력 조회"""
        return self.db.get_prices(code, hours=hours)

    def get_trade_history(self, code: str, hours: int = 24) -> List[Dict]:
        """거래 이력 조회"""
        return self.db.get_trades(code, hours=hours)

    def calculate_moving_average(self, code: str, periods: int = 20, hours: int = 24) -> Optional[float]:
        """이동평균 계산"""
        prices = self.get_price_history(code, hours=hours)
        if len(prices) < periods:
            return None

        recent_prices = [p["price"] for p in prices[-periods:]]
        return sum(recent_prices) / len(recent_prices)

    def calculate_daily_statistics(self, code: str) -> Dict:
        """일일 통계 계산"""
        today = datetime.now().strftime("%Y-%m-%d")
        summary = self.db.get_daily_summary(code, today)

        if not summary:
            return {
                "code": code,
                "date": today,
                "min_price": None,
                "max_price": None,
                "total_volume": 0,
                "total_foreign_net": 0,
                "total_institution_net": 0,
            }

        return summary

    def get_volatility(self, code: str, hours: int = 24) -> Optional[float]:
        """변동성 계산 (표준편차)"""
        prices = self.get_price_history(code, hours=hours)
        if len(prices) < 2:
            return None

        price_list = [p["price"] for p in prices]
        return statistics.stdev(price_list)

    def get_price_range(self, code: str, hours: int = 24) -> Dict[str, float]:
        """가격 범위 조회"""
        prices = self.get_price_history(code, hours=hours)

        if not prices:
            return {"min": None, "max": None, "range": None}

        price_list = [p["price"] for p in prices]
        min_price = min(price_list)
        max_price = max(price_list)

        return {
            "min": min_price,
            "max": max_price,
            "range": max_price - min_price
        }

    def get_foreign_institution_summary(self, code: str, hours: int = 24) -> Dict:
        """외국인/기관 매매 요약"""
        trades = self.get_trade_history(code, hours=hours)

        if not trades:
            return {
                "code": code,
                "total_foreign_buy": 0,
                "total_foreign_sell": 0,
                "total_institution_buy": 0,
                "total_institution_sell": 0,
                "net_foreign": 0,
                "net_institution": 0,
            }

        total_foreign_buy = sum(t.get("foreign_buy_volume", 0) for t in trades)
        total_foreign_sell = sum(t.get("foreign_sell_volume", 0) for t in trades)
        total_institution_buy = sum(t.get("institution_buy_volume", 0) for t in trades)
        total_institution_sell = sum(t.get("institution_sell_volume", 0) for t in trades)

        return {
            "code": code,
            "total_foreign_buy": total_foreign_buy,
            "total_foreign_sell": total_foreign_sell,
            "total_institution_buy": total_institution_buy,
            "total_institution_sell": total_institution_sell,
            "net_foreign": total_foreign_buy - total_foreign_sell,
            "net_institution": total_institution_buy - total_institution_sell,
        }

    def analyze_trend(self, code: str, hours: int = 24) -> Dict:
        """추세 분석"""
        prices = self.get_price_history(code, hours=hours)

        if len(prices) < 2:
            return {"trend": "insufficient_data"}

        first_price = prices[0]["price"]
        last_price = prices[-1]["price"]
        change = ((last_price - first_price) / first_price) * 100

        return {
            "code": code,
            "period_hours": hours,
            "start_price": first_price,
            "end_price": last_price,
            "change_percent": round(change, 2),
            "trend": "up" if change > 0 else "down",
            "total_candles": len(prices),
        }

    def get_real_time_data(self) -> Dict:
        """실시간 데이터 조회 (캐시된 최신 데이터)"""
        return self.latest_data.copy()

    def cleanup_old_data(self, retention_days: int = None) -> int:
        """오래된 데이터 정리"""
        return self.db.cleanup_old_data(retention_days)

    def is_running(self) -> bool:
        """서비스 실행 상태"""
        return self.running and self.api_client.health_check()
