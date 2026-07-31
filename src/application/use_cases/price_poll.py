import asyncio
import time
from decimal import Decimal

import structlog

from application.dto.price_record import PriceRecordDTO
from application.interfaces.deribit_client import IDeribitAPIClient
from application.interfaces.price_record_repository import IPriceRecordRepository
from domain.tickers import Ticker

logger = structlog.get_logger(__name__)


class PricePollUseCase:
    """Use case для опроса api."""

    def __init__(
        self,
        repo: IPriceRecordRepository,
        api_client: IDeribitAPIClient,
        supported_tickets: set[Ticker],
    ) -> None:
        self._repo = repo
        self._api_client = api_client
        self._supported_tickers = supported_tickets

    async def execute(self) -> None:
        timestamp = int(time.time())

        results: list[BaseException | Decimal] = await asyncio.gather(
            *(
                self._api_client.get_currency_price(ticket)
                for ticket in self._supported_tickers
            ),
            return_exceptions=True,
        )

        records: list[PriceRecordDTO] = []

        for ticker, result in zip(
            self._supported_tickers,
            results,
            strict=True,
        ):
            if isinstance(result, BaseException):
                logger.warning(
                    "Ошибка при получении цены", error=str(result), ticker=ticker
                )
            else:
                records.append(
                    PriceRecordDTO(ticker=ticker, price=result, timestamp=timestamp)
                )

        if not records:
            logger.warning("Не был получено цен валют")
            return

        logger.info("Записи о цене успешно получены")
        await self._repo.add_records(records)
        logger.info("Записи о цене успешно сохранены")
