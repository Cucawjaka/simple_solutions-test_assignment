from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from errors.application import PriceRecordsNotFoundError
from infrastructure.web_server.exception_handlers import (
    price_records_not_found_exception_handler,
)
from infrastructure.web_server.routers import router


def create_app(container: AsyncContainer) -> FastAPI:
    """Создает FastAPI приложение.

    Args:
        container (AsyncContainer): IoC контейнер

    Returns:
        FastAPI: FastAPI приложение

    """
    app = FastAPI(docs_url="/docs")

    setup_dishka(container=container, app=app)

    app.include_router(router)

    app.exception_handler(PriceRecordsNotFoundError)(
        price_records_not_found_exception_handler
    )

    return app
