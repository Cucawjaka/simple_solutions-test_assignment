from dataclasses import dataclass
from decimal import Decimal

from domain.tickers import Ticker


@dataclass(frozen=True, slots=True)
class PriceRecordDTO:
    """DTO для представления записи о цене."""

    ticker: Ticker
    price: Decimal
    timestamp: int
