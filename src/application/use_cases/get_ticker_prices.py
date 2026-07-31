from application.dto.price_record import PriceRecordDTO
from application.interfaces.price_record_repository import IPriceRecordRepository
from domain.tickers import Ticker


class GetTickerPricesUseCase:
    def __init__(self, repo: IPriceRecordRepository) -> None:
        self._repo = repo

    async def execute(
        self,
        ticker: Ticker,
        limit: int,
        offset: int,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
    ) -> list[PriceRecordDTO]:
        return await self._repo.get_all(
            ticker=ticker,
            limit=limit,
            offset=offset,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
        )
