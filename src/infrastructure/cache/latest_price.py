import json
from decimal import Decimal, InvalidOperation

import structlog
from redis.asyncio import Redis
from redis.exceptions import RedisError

from application.dto.price_record import PriceRecordDTO
from application.interfaces.latest_price_cache import ILatestPriceCache
from domain.tickers import Ticker
from errors.application import IntegrationError

logger = structlog.get_logger(__name__)


class RedisLatestPriceCache(ILatestPriceCache):
    """Redis-реализация кэша последней цены тикера."""

    def __init__(self, redis_client: Redis) -> None:
        self._redis_client = redis_client

    async def get_latest_price(self, ticker: Ticker) -> PriceRecordDTO | None:
        try:
            cached_value = await self._redis_client.get(self._build_key(ticker))
        except RedisError as e:
            logger.warning("Ошибка при чтении последней цены из Redis", error=str(e))
            raise IntegrationError("Ошибка при работе с Redis")

        if cached_value is None:
            return None

        try:
            payload = json.loads(cached_value)
            return PriceRecordDTO(
                ticker=Ticker(payload["ticker"]),
                price=Decimal(payload["price"]),
                timestamp=int(payload["timestamp"]),
            )
        except (KeyError, TypeError, ValueError, InvalidOperation) as e:
            logger.warning(
                "Redis вернул поврежденное значение последней цены",
                error=str(e),
                ticker=ticker.value,
            )
            return None

    async def set_latest_price(self, record: PriceRecordDTO) -> None:
        payload = json.dumps(
            {
                "ticker": record.ticker.value,
                "price": str(record.price),
                "timestamp": record.timestamp,
            }
        )

        try:
            await self._redis_client.set(self._build_key(record.ticker), payload)
        except RedisError as e:
            logger.warning("Ошибка при записи последней цены в Redis", error=str(e))
            raise IntegrationError("Ошибка при работе с Redis")

    @staticmethod
    def _build_key(ticker: Ticker) -> str:
        return f"latest_price:{ticker.value}"
