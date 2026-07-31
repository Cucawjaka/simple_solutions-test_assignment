from typing import Protocol

from application.dto.price_record import PriceRecordDTO
from domain.tickers import Ticker


class IPriceRecordRepository(Protocol):
    """Интерфейс репозитория для работы с ценами."""

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
        ...

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
        ...
