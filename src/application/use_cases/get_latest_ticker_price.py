from application.dto.price_record import PriceRecordDTO
from application.interfaces.price_record_repository import IPriceRecordRepository
from domain.tickers import Ticker
from errors.application import PriceRecordsNotFoundError


class GetLatestTickerPriceUseCase:
    def __init__(self, repo: IPriceRecordRepository) -> None:
        self._repo = repo

    async def execute(self, ticker: Ticker) -> PriceRecordDTO:
        record = await self._repo.get_latest_price(ticker)

        if record is None:
            raise PriceRecordsNotFoundError(msg="Записи по тикету не найдены")

        return record
