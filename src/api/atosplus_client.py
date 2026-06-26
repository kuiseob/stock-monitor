import websocket
import json
import threading
import time
from typing import Callable, Optional, List
from datetime import datetime
from queue import Queue
from src.api.models import StockPrice, ForexInstitutionalTrade
from src.utils.logger import setup_logger
from src.utils.config import Config

logger = setup_logger(__name__)

class AtosplusClient:
    """삼성증권 Atosplus WebSocket 클라이언트"""

    def __init__(self, api_key: str, account_id: str, ws_url: str):
        self.api_key = api_key
        self.account_id = account_id
        self.ws_url = ws_url
        self.ws = None
        self.connected = False
        self.retry_count = 0
        self.retry_delay = 1
        self.max_retries = 5
        self.data_queue = Queue()
        self.message_queue = Queue()
        self.running = False
        self.callbacks = {}  # 이벤트별 콜백

    def on_price_update(self, callback: Callable) -> None:
        """가격 업데이트 콜백 등록"""
        self.callbacks["price_update"] = callback

    def on_trade_update(self, callback: Callable) -> None:
        """거래 업데이트 콜백 등록"""
        self.callbacks["trade_update"] = callback

    def on_error(self, callback: Callable) -> None:
        """에러 콜백 등록"""
        self.callbacks["error"] = callback

    def connect(self) -> bool:
        """WebSocket 연결"""
        try:
            logger.info(f"Connecting to {self.ws_url}")
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
            )
            self.running = True
            self.ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            self.ws_thread.start()
            time.sleep(2)  # 연결 안정화 대기
            self.connected = True
            self.retry_count = 0
            logger.info("Connected to Atosplus WebSocket")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def connect_with_retry(self) -> bool:
        """재시도 로직을 포함한 연결"""
        while self.retry_count < self.max_retries:
            if self.connect():
                return True
            self.retry_count += 1
            logger.warning(
                f"Retry {self.retry_count}/{self.max_retries} "
                f"in {self.retry_delay}s"
            )
            time.sleep(self.retry_delay)
            self.retry_delay = min(self.retry_delay * 2, 30)
        return False

    def disconnect(self) -> None:
        """연결 해제"""
        self.running = False
        if self.ws:
            self.ws.close()
        logger.info("Disconnected from Atosplus WebSocket")

    def subscribe_prices(self, stock_codes: List[str]) -> None:
        """종목 실시간 가격 구독"""
        message = {
            "method": "subscribe",
            "params": {
                "codes": stock_codes,
                "types": ["price"]
            }
        }
        self.send_message(message)

    def subscribe_trades(self, stock_codes: List[str]) -> None:
        """종목 거래 정보(외국인/기관) 구독"""
        message = {
            "method": "subscribe",
            "params": {
                "codes": stock_codes,
                "types": ["trade"]
            }
        }
        self.send_message(message)

    def send_message(self, message: dict) -> None:
        """메시지 송신"""
        try:
            if self.ws:
                self.ws.send(json.dumps(message))
                logger.debug(f"Message sent: {message}")
        except Exception as e:
            logger.error(f"Failed to send message: {e}")

    def _on_open(self, ws):
        """WebSocket 연결 시작"""
        logger.info("WebSocket opened")
        # 인증 메시지
        auth_message = {
            "method": "auth",
            "params": {
                "api_key": self.api_key,
                "account_id": self.account_id
            }
        }
        self.send_message(auth_message)

    def _on_message(self, ws, message: str) -> None:
        """메시지 수신"""
        try:
            data = json.loads(message)
            self._process_message(data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def _process_message(self, data: dict) -> None:
        """메시지 처리"""
        msg_type = data.get("type", "")

        if msg_type == "price_update":
            self._handle_price_update(data)
        elif msg_type == "trade_update":
            self._handle_trade_update(data)
        elif msg_type == "error":
            self._handle_error(data)
        else:
            logger.debug(f"Unknown message type: {msg_type}")

    def _handle_price_update(self, data: dict) -> None:
        """가격 업데이트 처리"""
        try:
            price = StockPrice(
                code=data["code"],
                timestamp=datetime.fromisoformat(data["timestamp"]),
                price=float(data["price"]),
                volume=int(data.get("volume", 0)),
                bid=float(data.get("bid")) if "bid" in data else None,
                ask=float(data.get("ask")) if "ask" in data else None,
            )
            self.data_queue.put(("price", price))

            callback = self.callbacks.get("price_update")
            if callback:
                callback(price)
            logger.debug(f"Price update: {price.code} @ {price.price}")
        except Exception as e:
            logger.error(f"Error handling price update: {e}")

    def _handle_trade_update(self, data: dict) -> None:
        """거래 업데이트 처리"""
        try:
            trade = ForexInstitutionalTrade(
                code=data["code"],
                timestamp=datetime.fromisoformat(data["timestamp"]),
                foreign_buy_volume=int(data.get("foreign_buy_volume", 0)),
                foreign_sell_volume=int(data.get("foreign_sell_volume", 0)),
                institution_buy_volume=int(data.get("institution_buy_volume", 0)),
                institution_sell_volume=int(data.get("institution_sell_volume", 0)),
            )
            self.data_queue.put(("trade", trade))

            callback = self.callbacks.get("trade_update")
            if callback:
                callback(trade)
            logger.debug(f"Trade update: {trade.code} - Foreign: {trade.net_foreign}")
        except Exception as e:
            logger.error(f"Error handling trade update: {e}")

    def _handle_error(self, data: dict) -> None:
        """에러 처리"""
        error_msg = data.get("message", "Unknown error")
        logger.error(f"API Error: {error_msg}")

        callback = self.callbacks.get("error")
        if callback:
            callback(error_msg)

    def _on_error(self, ws, error):
        """WebSocket 에러"""
        logger.error(f"WebSocket error: {error}")
        self.connected = False

    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket 종료"""
        logger.warning(f"WebSocket closed: {close_msg}")
        self.connected = False

    def get_latest_data(self) -> dict:
        """최신 데이터 반환"""
        results = {}
        while not self.data_queue.empty():
            msg_type, data = self.data_queue.get()
            key = f"{msg_type}_{data.code}"
            results[key] = data
        return results

    def health_check(self) -> bool:
        """연결 상태 체크"""
        return self.connected and self.running
