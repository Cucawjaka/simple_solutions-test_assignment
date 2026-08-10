import asyncio

import httpx
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from application.use_cases.price_poll import PricePollUseCase
from config import DatabaseConfig, PollingConfig, RedisConfig
from infrastructure.cache.latest_price import RedisLatestPriceCache
from infrastructure.polling.celery import celery_app
from infrastructure.polling.client import DeribitAPIClient
from infrastructure.repositories.price_record import PriceRecordRepository


async def run_collect_prices() -> None:
    polling_config = PollingConfig()
    database_config = DatabaseConfig()
    redis_config = RedisConfig()

    engine = create_async_engine(
        database_config.sqlalchemy_url, echo=False, poolclass=NullPool
    )
    session_factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    redis_client = Redis.from_url(redis_config.broker_url, decode_responses=True)

    try:
        async with (
            httpx.AsyncClient(
                base_url=polling_config.api_url,
                timeout=10,
            ) as http_client,
            session_factory() as session,
        ):
            repository = PriceRecordRepository(session)
            deribit_client = DeribitAPIClient(http_client)
            latest_price_cache = RedisLatestPriceCache(redis_client)

            use_case = PricePollUseCase(
                cache=latest_price_cache,
                api_client=deribit_client,
                repo=repository,
                supported_tickets=polling_config.supported_tickers,
            )

            await use_case.execute()
    finally:
        await redis_client.aclose()
        await engine.dispose()


@celery_app.task(name="collect_prices", ignore_result=True)
def collect_prices_task() -> None:
    asyncio.run(run_collect_prices())
