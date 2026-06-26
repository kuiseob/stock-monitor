import sqlite3
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from src.api.models import StockPrice, ForexInstitutionalTrade
from src.utils.logger import setup_logger
from src.utils.config import Config

logger = setup_logger(__name__)

class DatabaseManager:
    """SQLite 데이터베이스 관리"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.lock = threading.Lock()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def init_database(self) -> None:
        """데이터베이스 초기화 및 스키마 생성"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            cursor = conn.cursor()

            # 주식 가격 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    price REAL NOT NULL,
                    volume INTEGER,
                    bid REAL,
                    ask REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(code, timestamp)
                )
            """)

            # 외국인/기관 거래 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    foreign_buy_volume INTEGER,
                    foreign_sell_volume INTEGER,
                    institution_buy_volume INTEGER,
                    institution_sell_volume INTEGER,
                    net_foreign INTEGER,
                    net_institution INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(code, timestamp)
                )
            """)

            # 인덱스 생성
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_prices_code_time
                ON stock_prices(code, timestamp DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_trades_code_time
                ON trades(code, timestamp DESC)
            """)

            conn.commit()
            logger.info(f"Database initialized: {self.db_path}")

    def insert_price(self, price: StockPrice) -> bool:
        """주식 가격 저장"""
        try:
            with self.lock, sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO stock_prices
                    (code, timestamp, price, volume, bid, ask)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    price.code,
                    price.timestamp,
                    price.price,
                    price.volume,
                    price.bid,
                    price.ask
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error inserting price: {e}")
            return False

    def insert_trade(self, trade: ForexInstitutionalTrade) -> bool:
        """거래 데이터 저장"""
        try:
            with self.lock, sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO trades
                    (code, timestamp, foreign_buy_volume, foreign_sell_volume,
                     institution_buy_volume, institution_sell_volume,
                     net_foreign, net_institution)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trade.code,
                    trade.timestamp,
                    trade.foreign_buy_volume,
                    trade.foreign_sell_volume,
                    trade.institution_buy_volume,
                    trade.institution_sell_volume,
                    trade.net_foreign,
                    trade.net_institution
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error inserting trade: {e}")
            return False

    def get_prices(self, code: str, hours: int = 24) -> List[Dict]:
        """지난 N시간의 가격 데이터 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cutoff_time = datetime.now() - timedelta(hours=hours)
                cursor.execute("""
                    SELECT code, timestamp, price, volume, bid, ask
                    FROM stock_prices
                    WHERE code = ? AND timestamp >= ?
                    ORDER BY timestamp ASC
                """, (code, cutoff_time))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error querying prices: {e}")
            return []

    def get_trades(self, code: str, hours: int = 24) -> List[Dict]:
        """지난 N시간의 거래 데이터 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cutoff_time = datetime.now() - timedelta(hours=hours)
                cursor.execute("""
                    SELECT code, timestamp, foreign_buy_volume, foreign_sell_volume,
                           institution_buy_volume, institution_sell_volume,
                           net_foreign, net_institution
                    FROM trades
                    WHERE code = ? AND timestamp >= ?
                    ORDER BY timestamp ASC
                """, (code, cutoff_time))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error querying trades: {e}")
            return []

    def get_daily_summary(self, code: str, date: str) -> Dict:
        """특정 날짜의 일일 통계"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 당일 데이터 조회
                cursor.execute("""
                    SELECT
                        COUNT(*) as trade_count,
                        MIN(price) as min_price,
                        MAX(price) as max_price,
                        SUM(volume) as total_volume,
                        SUM(net_foreign) as total_foreign_net,
                        SUM(net_institution) as total_institution_net
                    FROM stock_prices sp
                    LEFT JOIN trades t ON sp.code = t.code
                    WHERE sp.code = ? AND DATE(sp.timestamp) = ?
                """, (code, date))
                result = cursor.fetchone()
                return {
                    "code": code,
                    "date": date,
                    "min_price": result[1],
                    "max_price": result[2],
                    "total_volume": result[3] or 0,
                    "total_foreign_net": result[4] or 0,
                    "total_institution_net": result[5] or 0,
                } if result else None
        except Exception as e:
            logger.error(f"Error querying daily summary: {e}")
            return None

    def cleanup_old_data(self, retention_days: int = None) -> int:
        """오래된 데이터 삭제"""
        retention_days = retention_days or Config.RETENTION_DAYS
        try:
            with self.lock, sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_date = datetime.now() - timedelta(days=retention_days)

                # 이전 데이터 삭제
                cursor.execute(
                    "DELETE FROM stock_prices WHERE timestamp < ?",
                    (cutoff_date,)
                )
                prices_deleted = cursor.rowcount

                cursor.execute(
                    "DELETE FROM trades WHERE timestamp < ?",
                    (cutoff_date,)
                )
                trades_deleted = cursor.rowcount

                conn.commit()
                logger.info(
                    f"Cleanup completed: "
                    f"{prices_deleted} prices, {trades_deleted} trades deleted"
                )
                return prices_deleted + trades_deleted
        except Exception as e:
            logger.error(f"Error cleaning up data: {e}")
            return 0

    def get_latest_price(self, code: str) -> Dict:
        """가장 최신 가격 데이터"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT code, timestamp, price, volume, bid, ask
                    FROM stock_prices
                    WHERE code = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (code,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error querying latest price: {e}")
            return None

    def get_latest_trade(self, code: str) -> Dict:
        """가장 최신 거래 데이터"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT code, timestamp, foreign_buy_volume, foreign_sell_volume,
                           institution_buy_volume, institution_sell_volume,
                           net_foreign, net_institution
                    FROM trades
                    WHERE code = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (code,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error querying latest trade: {e}")
            return None

    def health_check(self) -> bool:
        """DB 연결 상태 확인"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
