from collections.abc import AsyncGenerator

import structlog
from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from application.interfaces.latest_price_cache import ILatestPriceCache
from application.interfaces.price_record_repository import IPriceRecordRepository
from application.use_cases.get_latest_ticker_price import GetLatestTickerPriceUseCase
from application.use_cases.get_ticker_prices import GetTickerPricesUseCase
from config import DatabaseConfig, RedisConfig
from infrastructure.cache.latest_price import RedisLatestPriceCache
from infrastructure.repositories.price_record import PriceRecordRepository

logger = structlog.getLogger(__name__)


class UseCasesProvider(Provider):
    """Провайдер для разрешения зависимостей, связанных с use cases."""

    @provide(scope=Scope.APP)
    def database_config(self) -> DatabaseConfig:
        """Создает и возвращает экземпляр конфигурации подключения к бд.

        Returns
            DatabaseConfig: объект с настройками клиентов.

        """
        try:
            config = DatabaseConfig()
        except Exception as e:
            logger.exception("Ошибка при загрузке конфигурации", error=str(e))
            raise
        return config

    @provide(scope=Scope.APP)
    def redis_config(self) -> RedisConfig:
        """Создает и возвращает экземпляр конфигурации Redis."""
        try:
            config = RedisConfig()
        except Exception as e:
            logger.exception("Ошибка при загрузке конфигурации", error=str(e))
            raise
        return config

    @provide(scope=Scope.APP)
    async def engine(self, config: DatabaseConfig) -> AsyncGenerator[AsyncEngine, None]:
        """Фабрика для создания экземпляра AsyncEngine."""
        engine = create_async_engine(config.sqlalchemy_url, echo=False)

        try:
            yield engine
        finally:
            await engine.dispose()

    @provide(scope=Scope.APP)
    async def redis_client(
        self, config: RedisConfig
    ) -> AsyncGenerator[Redis, None]:
        """Фабрика для создания Redis-клиента."""
        client = Redis.from_url(config.broker_url, decode_responses=True)

        try:
            yield client
        finally:
            await client.aclose()

    @provide(scope=Scope.APP)
    def session_maker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        """Фабрика для создания экземпляра AsyncSession."""
        return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    @provide(scope=Scope.REQUEST)
    async def session(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncGenerator[AsyncSession, None]:
        """Фабрика для создания экземпляра AsyncSession."""
        async with session_maker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def price_record_repository(self, session: AsyncSession) -> IPriceRecordRepository:
        """Фабрика для создания экземпляра PriceRecordRepository.

        Returns
            IPriceRecordRepository: экземпляр PriceRecordRepository.

        """
        return PriceRecordRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def latest_price_cache(self, redis_client: Redis) -> ILatestPriceCache:
        """Фабрика для создания экземпляра RedisLatestPriceCache."""
        return RedisLatestPriceCache(redis_client=redis_client)

    @provide(scope=Scope.REQUEST)
    def get_ticker_prices_use_case(
        self, repo: IPriceRecordRepository
    ) -> GetTickerPricesUseCase:
        """Фабрика для создания экземпляра GetTickerPricesUseCase.

        Args:
            repo (IPriceRecordRepository): репозиторий для работы с историей цен валют

        Returns:
            GetTickerPricesUseCase: экземпляр GetTickerPricesUseCase.

        """
        return GetTickerPricesUseCase(repo=repo)

    @provide(scope=Scope.REQUEST)
    def link_untrack_use_case(
        self, repo: IPriceRecordRepository, cache: ILatestPriceCache
    ) -> GetLatestTickerPriceUseCase:
        """Фабрика для создания экземпляра GetLatestTickerPriceUseCase.

        Args:
            repo (IPriceRecordRepository): репозиторий для работы с историей цен валют

        Returns:
            GetLatestTickerPriceUseCase: экземпляр GetLatestTickerPriceUseCase.

        """
        return GetLatestTickerPriceUseCase(repo=repo, cache=cache)
