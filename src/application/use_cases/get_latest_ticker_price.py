import structlog

from application.dto.price_record import PriceRecordDTO
from application.interfaces.latest_price_cache import ILatestPriceCache
from application.interfaces.price_record_repository import IPriceRecordRepository
from domain.tickers import Ticker
from errors.application import IntegrationError, PriceRecordsNotFoundError

logger = structlog.get_logger(__name__)


class GetLatestTickerPriceUseCase:
    def __init__(
        self, repo: IPriceRecordRepository, cache: ILatestPriceCache
    ) -> None:
        self._repo = repo
        self._cache = cache

    async def execute(self, ticker: Ticker) -> PriceRecordDTO:
        try:
            cached_record = await self._cache.get_latest_price(ticker)
        except IntegrationError as e:
            logger.warning(
                "Не удалось получить последнюю цену из кэша",
                error=str(e),
                ticker=ticker.value,
            )
        else:
            if cached_record is not None:
                return cached_record

        record = await self._repo.get_latest_price(ticker)

        if record is None:
            raise PriceRecordsNotFoundError(msg="Записи по тикету не найдены")

        try:
            await self._cache.set_latest_price(record)
        except IntegrationError as e:
            logger.warning(
                "Не удалось сохранить последнюю цену в кэш",
                error=str(e),
                ticker=ticker.value,
            )

        return record
