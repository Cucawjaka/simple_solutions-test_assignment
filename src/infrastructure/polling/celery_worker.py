import asyncio

import httpx
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from application.use_cases.price_poll import PricePollUseCase
from config import DatabaseConfig, PollingConfig
from infrastructure.polling.celery import celery_app
from infrastructure.polling.client import DeribitAPIClient
from infrastructure.repositories.price_record import PriceRecordRepository


async def run_collect_prices() -> None:
    polling_config = PollingConfig()
    database_config = DatabaseConfig()

    engine = create_async_engine(
        database_config.sqlalchemy_url, echo=False, poolclass=NullPool
    )
    session_factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

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

            use_case = PricePollUseCase(
                api_client=deribit_client,
                repo=repository,
                supported_tickets=polling_config.supported_tickers,
            )

            await use_case.execute()
    finally:
        await engine.dispose()


@celery_app.task(name="collect_prices", ignore_result=True)
def collect_prices_task() -> None:
    asyncio.run(run_collect_prices())
