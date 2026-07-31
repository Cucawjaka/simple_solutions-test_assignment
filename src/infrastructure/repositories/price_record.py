import structlog
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from application.dto.price_record import PriceRecordDTO
from domain.tickers import Ticker
from errors.application import IntegrationError, TickerNotFoundError
from infrastructure.db.models import PriceRecordModel, TickerModel

logger = structlog.get_logger(__name__)


class PriceRecordRepository:
    """Репозиторий для работы с ценами."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_records(self, records: list[PriceRecordDTO]) -> None:
        """Сохраняет записи о ценах валют в базу данных.

        Args:
            records (list[PriceRecordDTO]): список dto с информацией о ценах
                валют

        Raises:
            TickerNotFoundError: при попытке добавления цены неподдерживаемой
                валюты
            IntegrationError: при ошибках работы с базой данных

        """
        ticker_names = [record.ticker.value for record in records]

        try:
            result = await self._session.execute(
                select(TickerModel.name, TickerModel.id).where(
                    TickerModel.name.in_(ticker_names),
                )
            )
        except SQLAlchemyError as e:
            logger.warning("Ошибка при работе с базой данных", error=str(e))
            raise IntegrationError("Ошибка при работе с базой данных")

        ticker_ids: dict[str, int] = {
            ticker_name: ticker_id for ticker_name, ticker_id in result
        }

        missing_tickers = set(ticker_names) - ticker_ids.keys()
        if missing_tickers:
            raise TickerNotFoundError(msg="Тикер не существует")

        models = [
            PriceRecordModel(
                ticker_id=ticker_ids[record.ticker.value],
                price=record.price,
                timestamp=record.timestamp,
            )
            for record in records
        ]

        try:
            self._session.add_all(models)
            await self._session.commit()
        except SQLAlchemyError as e:
            logger.warning("Ошибка при работе с базой данных", error=str(e))
            await self._session.rollback()
            raise IntegrationError("Ошибка при работе с базой данных")

    async def get_all(
        self,
        ticker: Ticker,
        limit: int,
        offset: int,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
    ) -> list[PriceRecordDTO]:
        """Получает записи о ценах валюты.

        Args:
            ticker (Ticker): тикер валюты
            limit (int): количество записей в ответе
            offset (int): количество записей, которые необходимо пропустить
            from_timestamp (int | None, optional): минимальный фильтр по
                дате. Defaults to None.
            to_timestamp (int | None, optional): максимальный фильтр по
                дате. Defaults to None.

        Returns:
            list[PriceRecordDTO]: список записей о цене тикера

        Raises:
            IntegrationError: при ошибках работы с базой данных

        """
        statement = (
            select(PriceRecordModel)
            .join(PriceRecordModel.ticker)
            .where(TickerModel.name == ticker.value)
            .order_by(PriceRecordModel.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )

        if from_timestamp is not None:
            statement = statement.where(PriceRecordModel.timestamp >= from_timestamp)

        if to_timestamp is not None:
            statement = statement.where(PriceRecordModel.timestamp <= to_timestamp)

        try:
            result = await self._session.scalars(statement)
        except SQLAlchemyError as e:
            logger.warning("Ошибка при работе с базой данных", error=str(e))
            raise IntegrationError("Ошибка при работе с базой данных")

        return [
            PriceRecordDTO(ticker=ticker, price=model.price, timestamp=model.timestamp)
            for model in result.all()
        ]

    async def get_latest_price(self, ticker: Ticker) -> PriceRecordDTO | None:
        """Получает последнюю цену валюты.

        Args:
            ticker (Ticker): тикер валюты

        Returns:
            PriceRecordDTO | None: запись о цене, None, если записи по
                текущей валюте отсутствуют

        Raises:
            IntegrationError: при ошибках работы с базой данных

        """
        statement = (
            select(PriceRecordModel)
            .join(PriceRecordModel.ticker)
            .where(TickerModel.name == ticker.value)
            .order_by(PriceRecordModel.timestamp.desc())
            .limit(1)
        )

        try:
            model = await self._session.scalar(statement)
        except SQLAlchemyError as e:
            logger.warning("Ошибка при работе с базой данных", error=str(e))
            raise IntegrationError("Ошибка при работе с базой данных")

        if model is None:
            return None

        return PriceRecordDTO(
            ticker=ticker,
            price=model.price,
            timestamp=model.timestamp,
        )
