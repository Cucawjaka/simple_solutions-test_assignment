from decimal import Decimal

from pydantic import BaseModel

from domain.tickers import Ticker


class TickerPriceResponse(BaseModel):
    """Цена тикера в определённый момент времени."""

    ticker: Ticker
    price: Decimal
    timestamp: int


class TickerPricesResponse(BaseModel):
    """Список цен тикера."""

    ticker_prices: list[TickerPriceResponse]
