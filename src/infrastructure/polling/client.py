import json
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx
import structlog

from domain.tickers import Ticker
from errors.application import IntegrationError

logger = structlog.get_logger(__name__)


INDEX_NAME_PARAM = "index_name"
INDEX_PRICE_API_METHOD = "get_index_price"

ERROR_FIELD_NAME = "error"
ERROR_MESSAGE_FIELD_NAME = "message"
ERROR_CODE_FIELD_NAME = "code"
ERROR_DATA_FIELD_NAME = "data"

RESULT_FIELD_NAME = "result"
PRICE_FIELD_NAME = "index_price"


class DeribitAPIClient:
    """Клиент для работы с api deribit.com."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def get_currency_price(self, ticker: Ticker) -> Decimal:
        """Получает цену валюты с биржи deribit.com.

        Args:
            ticker (Ticker): тикер валюты

        Raises:
            IntegrationError: при ошибках интеграции с внешними сервисами

        Returns:
            Decimal: цена валюты

        """
        try:
            response = await self._client.get(
                url=INDEX_PRICE_API_METHOD, params={INDEX_NAME_PARAM: ticker.value}
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            msg = "Ошибка при запросе к API deribit.com"
            logger.warning(
                msg,
                method=INDEX_PRICE_API_METHOD,
                error=str(e),
                ticker=ticker.value,
            )

            raise IntegrationError(msg=msg)

        try:
            data: dict[str, Any] = response.json()
        except json.JSONDecodeError as e:
            msg = "API deribit.com вернул некорректный JSON"

            logger.warning(
                msg,
                method=INDEX_PRICE_API_METHOD,
                ticker=ticker.value,
                error=str(e),
            )

            raise IntegrationError(msg=msg)

        if error := data.get(ERROR_FIELD_NAME):
            msg = "Ошибка при запросе к API deribit.com"
            logger.warning(
                msg,
                method=INDEX_PRICE_API_METHOD,
                error=error.get(ERROR_MESSAGE_FIELD_NAME),
                code=error.get(ERROR_CODE_FIELD_NAME),
                data=error.get(ERROR_DATA_FIELD_NAME),
            )

            raise IntegrationError(msg=msg)

        try:
            raw_price = data[RESULT_FIELD_NAME][PRICE_FIELD_NAME]
            return Decimal(str(raw_price))
        except (KeyError, TypeError, InvalidOperation) as e:
            msg = "API deribit.com вернул ответ неожиданного формата"

            logger.warning(
                msg,
                method=INDEX_PRICE_API_METHOD,
                ticker=ticker.value,
                response_data=data,
                error=str(e),
            )

            raise IntegrationError(msg=msg)
