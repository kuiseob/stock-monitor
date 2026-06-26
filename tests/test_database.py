import unittest
import sqlite3
from datetime import datetime
from pathlib import Path
import sys
import os
import tempfile

# 부모 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.manager import DatabaseManager
from src.api.models import StockPrice, ForexInstitutionalTrade

class TestDatabaseManager(unittest.TestCase):
    """데이터베이스 매니저 테스트"""

    def setUp(self):
        """테스트 전 설정 (임시 파일 DB 사용)"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        self.db = DatabaseManager(self.db_path)

    def tearDown(self):
        """테스트 후 정리"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_init_database(self):
        """DB 초기화 테스트"""
        # 테이블 존재 확인
        with sqlite3.connect(":memory:") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

    def test_insert_price(self):
        """가격 데이터 삽입 테스트"""
        price = StockPrice(
            code="005930",
            timestamp=datetime.now(),
            price=70500.0,
            volume=1000000,
            bid=70490.0,
            ask=70510.0
        )
        result = self.db.insert_price(price)
        self.assertTrue(result)

    def test_insert_trade(self):
        """거래 데이터 삽입 테스트"""
        trade = ForexInstitutionalTrade(
            code="005930",
            timestamp=datetime.now(),
            foreign_buy_volume=100000,
            foreign_sell_volume=50000,
            institution_buy_volume=80000,
            institution_sell_volume=60000
        )
        result = self.db.insert_trade(trade)
        self.assertTrue(result)

    def test_get_latest_price(self):
        """최신 가격 조회 테스트"""
        now = datetime.now()
        price = StockPrice(
            code="005930",
            timestamp=now,
            price=70500.0,
            volume=1000000
        )
        self.db.insert_price(price)

        latest = self.db.get_latest_price("005930")
        self.assertIsNotNone(latest)
        self.assertEqual(latest["code"], "005930")
        self.assertEqual(latest["price"], 70500.0)

    def test_get_prices(self):
        """시간범위 가격 조회 테스트"""
        now = datetime.now()
        for i in range(5):
            price = StockPrice(
                code="005930",
                timestamp=now,
                price=70500.0 + i * 100,
                volume=1000000 + i * 10000
            )
            self.db.insert_price(price)

        prices = self.db.get_prices("005930", hours=24)
        self.assertGreaterEqual(len(prices), 1)

    def test_health_check(self):
        """DB 상태 확인 테스트"""
        is_healthy = self.db.health_check()
        self.assertTrue(is_healthy)

if __name__ == "__main__":
    unittest.main()
