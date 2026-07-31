from decimal import Decimal
from typing import Protocol

from domain.tickers import Ticker


class IDeribitAPIClient(Protocol):
    """Интерфейс клиента для работы с api deribit.com."""

    async def get_currency_price(self, ticker: Ticker) -> Decimal:
        """Получает цену валюты с биржи deribit.com.

        Args:
            ticker (Ticker): тикер валюты

        Raises:
            IntegrationError: при ошибках интеграции с внешними сервисами

        Returns:
            Decimal: цена валюты

        """
        ...
