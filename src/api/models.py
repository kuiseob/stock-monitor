from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class StockPrice:
    """주식 가격 데이터"""
    code: str
    timestamp: datetime
    price: float
    volume: int
    bid: Optional[float] = None
    ask: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "timestamp": self.timestamp.isoformat(),
            "price": self.price,
            "volume": self.volume,
            "bid": self.bid,
            "ask": self.ask,
        }

@dataclass
class TradeData:
    """거래 데이터 (외국인/기관)"""
    code: str
    timestamp: datetime
    side: str  # "BUY" or "SELL"
    investor_type: str  # "FOREIGN" or "INSTITUTION"
    volume: int
    price: float

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "timestamp": self.timestamp.isoformat(),
            "side": self.side,
            "investor_type": self.investor_type,
            "volume": self.volume,
            "price": self.price,
        }

@dataclass
class ForexInstitutionalTrade:
    """외국인/기관 누적 거래 데이터"""
    code: str
    timestamp: datetime
    foreign_buy_volume: int
    foreign_sell_volume: int
    institution_buy_volume: int
    institution_sell_volume: int
    net_foreign: Optional[int] = None
    net_institution: Optional[int] = None

    def __post_init__(self):
        """계산된 필드 초기화"""
        if self.net_foreign is None:
            self.net_foreign = self.foreign_buy_volume - self.foreign_sell_volume
        if self.net_institution is None:
            self.net_institution = self.institution_buy_volume - self.institution_sell_volume

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "timestamp": self.timestamp.isoformat(),
            "foreign_buy_volume": self.foreign_buy_volume,
            "foreign_sell_volume": self.foreign_sell_volume,
            "institution_buy_volume": self.institution_buy_volume,
            "institution_sell_volume": self.institution_sell_volume,
            "net_foreign": self.net_foreign,
            "net_institution": self.net_institution,
        }
