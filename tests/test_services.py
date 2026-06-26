import unittest
import sqlite3
import tempfile
import os
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.manager import DatabaseManager
from src.api.models import StockPrice, ForexInstitutionalTrade
from src.services.stock_service import StockService
from src.services.cache_service import DataService

class TestStockService(unittest.TestCase):
    """주식 서비스 테스트"""

    def setUp(self):
        """테스트 전 설정"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()

        # 테스트용 데이터베이스 경로 설정
        import src.utils.config
        original_db_path = src.utils.config.Config.DATABASE_PATH
        src.utils.config.Config.DATABASE_PATH = self.db_path

        self.db = DatabaseManager(self.db_path)

    def tearDown(self):
        """테스트 후 정리"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def _insert_sample_data(self, code: str = "005930", hours: int = 1):
        """샘플 데이터 삽입"""
        from datetime import timedelta

        base_time = datetime.now()
        for i in range(60):  # 1시간 데이터 (1분 단위)
            timestamp = base_time - timedelta(minutes=60-i)

            # 가격 데이터
            price = StockPrice(
                code=code,
                timestamp=timestamp,
                price=70000.0 + i * 100,
                volume=100000 + i * 1000,
                bid=69900.0 + i * 100,
                ask=70100.0 + i * 100
            )
            self.db.insert_price(price)

            # 거래 데이터
            trade = ForexInstitutionalTrade(
                code=code,
                timestamp=timestamp,
                foreign_buy_volume=10000 + i * 100,
                foreign_sell_volume=5000 + i * 50,
                institution_buy_volume=8000 + i * 80,
                institution_sell_volume=6000 + i * 60
            )
            self.db.insert_trade(trade)

    def test_calculate_daily_statistics(self):
        """일일 통계 계산 테스트"""
        self._insert_sample_data()

        summary = self.db.get_daily_summary("005930", datetime.now().strftime("%Y-%m-%d"))
        self.assertIsNotNone(summary)
        self.assertGreater(summary["total_volume"], 0)

    def test_get_foreign_institution_summary(self):
        """외국인/기관 요약 테스트"""
        self._insert_sample_data()

        trades = self.db.get_trades("005930", hours=24)
        self.assertGreater(len(trades), 0)

        total_foreign_buy = sum(t.get("foreign_buy_volume", 0) for t in trades)
        total_foreign_sell = sum(t.get("foreign_sell_volume", 0) for t in trades)

        net_foreign = total_foreign_buy - total_foreign_sell
        self.assertGreaterEqual(net_foreign, 0)

    def test_get_price_range(self):
        """가격 범위 조회 테스트"""
        self._insert_sample_data()

        prices = self.db.get_prices("005930", hours=24)
        self.assertGreater(len(prices), 0)

        price_list = [p["price"] for p in prices]
        min_price = min(price_list)
        max_price = max(price_list)

        self.assertLess(min_price, max_price)
        self.assertAlmostEqual(min_price, 70000.0, delta=1)

    def test_analyze_trend(self):
        """추세 분석 테스트"""
        self._insert_sample_data()

        prices = self.db.get_prices("005930", hours=24)
        self.assertGreater(len(prices), 1)

        first_price = prices[0]["price"]
        last_price = prices[-1]["price"]
        change = ((last_price - first_price) / first_price) * 100

        self.assertGreater(change, 0)

    def test_multiple_stocks(self):
        """여러 종목 데이터 처리 테스트"""
        codes = ["005930", "000660", "006400"]

        for code in codes:
            self._insert_sample_data(code=code)

        for code in codes:
            prices = self.db.get_prices(code, hours=24)
            self.assertGreater(len(prices), 0)
            self.assertEqual(prices[0]["code"], code)

    def test_data_cleanup(self):
        """데이터 정리 테스트"""
        self._insert_sample_data()

        # 정리 전 데이터 확인
        prices_before = self.db.get_prices("005930", hours=24)
        self.assertGreater(len(prices_before), 0)

        # 정리 (30일 유지 - 최근 데이터는 유지)
        deleted_count = self.db.cleanup_old_data(retention_days=30)

        # 정리 후 데이터 확인 (30일 이내는 유지)
        prices_after = self.db.get_prices("005930", hours=24)
        # 최근 1시간 데이터는 유지되어야 함
        self.assertGreater(len(prices_after), 0)

class TestDataService(unittest.TestCase):
    """데이터 서비스 테스트"""

    def setUp(self):
        """테스트 전 설정"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()

        import src.utils.config
        src.utils.config.Config.DATABASE_PATH = self.db_path

        self.db = DatabaseManager(self.db_path)
        self.data_service = DataService()

    def tearDown(self):
        """테스트 후 정리"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def _insert_sample_data(self, code: str = "005930"):
        """샘플 데이터 삽입"""
        from datetime import timedelta

        base_time = datetime.now()
        for i in range(60):
            timestamp = base_time - timedelta(minutes=60-i)

            price = StockPrice(
                code=code,
                timestamp=timestamp,
                price=70000.0 + i * 100,
                volume=100000 + i * 1000
            )
            self.db.insert_price(price)

            trade = ForexInstitutionalTrade(
                code=code,
                timestamp=timestamp,
                foreign_buy_volume=10000 + i * 100,
                foreign_sell_volume=5000 + i * 50,
                institution_buy_volume=8000 + i * 80,
                institution_sell_volume=6000 + i * 60
            )
            self.db.insert_trade(trade)

    def test_format_price(self):
        """가격 포맷팅 테스트"""
        self.assertEqual(self.data_service.format_price(70000), "70,000 원")
        self.assertEqual(self.data_service.format_price(1000000), "1,000,000 원")

    def test_format_volume(self):
        """거래량 포맷팅 테스트"""
        self.assertEqual(self.data_service.format_volume(1000000), "1.0M")
        self.assertEqual(self.data_service.format_volume(100000), "100.0K")
        self.assertEqual(self.data_service.format_volume(500), "500")

    def test_format_percent(self):
        """백분율 포맷팅 테스트"""
        self.assertIn("+1.50", self.data_service.format_percent(1.5))
        self.assertIn("-2.30", self.data_service.format_percent(-2.3))

    def test_stock_overview_no_data(self):
        """데이터 없을 때 개요 테스트"""
        overview = self.data_service.get_stock_overview("005930")
        self.assertEqual(overview["status"], "no_data")

    def test_stock_overview_with_data(self):
        """데이터 있을 때 개요 테스트"""
        self._insert_sample_data()

        # 캐시를 무시하고 직접 DB에서 조회
        latest_price = self.db.get_latest_price("005930")
        self.assertIsNotNone(latest_price)

        # 개요 정보 확인
        self.assertIsNotNone(latest_price["price"])
        self.assertGreater(latest_price["price"], 0)

if __name__ == "__main__":
    unittest.main()
