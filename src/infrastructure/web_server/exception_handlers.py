import structlog
from fastapi import Request, status
from fastapi.responses import JSONResponse

from errors.application import PriceRecordsNotFoundError

logger = structlog.getLogger(__name__)


async def price_records_not_found_exception_handler(
    request: Request,
    exc: PriceRecordsNotFoundError,
) -> JSONResponse:
    logger.warning(
        "Записи о цене валюты не найдены",
        error=exc.msg,
        method=request.method,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": exc.msg,
        },
    )
