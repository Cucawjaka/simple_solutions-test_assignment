from typing import Protocol

from application.dto.price_record import PriceRecordDTO
from domain.tickers import Ticker


class ILatestPriceCache(Protocol):
    """Интерфейс кэша для работы с последней ценой тикера."""

    async def get_latest_price(self, ticker: Ticker) -> PriceRecordDTO | None:
        """Возвращает последнюю цену тикера из кэша, если она существует."""
        ...

    async def set_latest_price(self, record: PriceRecordDTO) -> None:
        """Сохраняет последнюю цену тикера в кэш."""
        ...
