import structlog
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query

from application.use_cases.get_latest_ticker_price import GetLatestTickerPriceUseCase
from application.use_cases.get_ticker_prices import GetTickerPricesUseCase
from domain.tickers import Ticker
from infrastructure.web_server.schemas import TickerPriceResponse, TickerPricesResponse

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/prices", route_class=DishkaRoute)


@router.get("", status_code=200, response_model=TickerPricesResponse)
async def get_ticker_prices(
    ticker: Ticker,
    use_case: FromDishka[GetTickerPricesUseCase],
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> TickerPricesResponse:
    logger.info("Запрос на получение всех данных о валюте", ticker=ticker)

    records = await use_case.execute(ticker=ticker, limit=limit, offset=offset)

    return TickerPricesResponse(
        ticker_prices=[
            TickerPriceResponse(
                ticker=record.ticker, price=record.price, timestamp=record.timestamp
            )
            for record in records
        ]
    )


@router.get(
    "/latest",
    status_code=200,
    response_model=TickerPriceResponse,
    responses={404: {"description": "Для тикера нет сохраненных цен"}},
)
async def get_latest_ticker_price(
    ticker: Ticker, use_case: FromDishka[GetLatestTickerPriceUseCase]
) -> TickerPriceResponse:
    logger.info("Запрос на получение последней цены валюты", ticker=ticker)

    record = await use_case.execute(ticker=ticker)

    return TickerPriceResponse(
        ticker=record.ticker, price=record.price, timestamp=record.timestamp
    )


@router.get("/by-date", status_code=200, response_model=TickerPricesResponse)
async def get_ticker_prices_by_date(
    ticker: Ticker,
    from_timestamp: int,
    to_timestamp: int,
    use_case: FromDishka[GetTickerPricesUseCase],
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> TickerPricesResponse:
    logger.info(
        "Запрос на получение данных о валюте с фильтром по дате",
        ticker=ticker,
        from_timestamp=from_timestamp,
        to_timestamp=to_timestamp,
    )

    records = await use_case.execute(
        ticker=ticker,
        limit=limit,
        offset=offset,
        from_timestamp=from_timestamp,
        to_timestamp=to_timestamp,
    )

    return TickerPricesResponse(
        ticker_prices=[
            TickerPriceResponse(
                ticker=record.ticker, price=record.price, timestamp=record.timestamp
            )
            for record in records
        ]
    )
