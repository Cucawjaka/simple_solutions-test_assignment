from decimal import Decimal

from pytest_mock import MockerFixture

from application.dto.price_record import PriceRecordDTO
from application.interfaces.deribit_client import IDeribitAPIClient
from application.interfaces.latest_price_cache import ILatestPriceCache
from application.interfaces.price_record_repository import IPriceRecordRepository
from application.use_cases.price_poll import PricePollUseCase
from domain.tickers import Ticker


async def test_saves_received_price(
    mocker: MockerFixture,
    repo_mock: IPriceRecordRepository,
    latest_price_cache_mock: ILatestPriceCache,
    api_client_mock: IDeribitAPIClient,
    supported_tickers: set[Ticker],
) -> None:
    timestamp = 1_722_424_800
    price = Decimal("118500.123")

    mocker.patch(
        "application.use_cases.price_poll.time.time",
        return_value=float(timestamp),
    )

    repo_mock.add_records = mocker.AsyncMock()
    latest_price_cache_mock.set_latest_price = mocker.AsyncMock()
    api_client_mock.get_currency_price = mocker.AsyncMock()
    api_client_mock.get_currency_price.return_value = price

    use_case = PricePollUseCase(
        repo=repo_mock,
        cache=latest_price_cache_mock,
        api_client=api_client_mock,
        supported_tickets=supported_tickers,
    )

    await use_case.execute()

    api_client_mock.get_currency_price.assert_awaited_once_with(Ticker.BTC_USD)

    repo_mock.add_records.assert_awaited_once_with(
        [PriceRecordDTO(ticker=Ticker.BTC_USD, price=price, timestamp=timestamp)]
    )
    latest_price_cache_mock.set_latest_price.assert_awaited_once_with(
        PriceRecordDTO(ticker=Ticker.BTC_USD, price=price, timestamp=timestamp)
    )


async def test_saves_only_successfully_received_prices(
    mocker: MockerFixture,
    repo_mock: IPriceRecordRepository,
    latest_price_cache_mock: ILatestPriceCache,
    api_client_mock: IDeribitAPIClient,
) -> None:
    timestamp = 1_722_424_800
    supported_tickers = {Ticker.BTC_USD, Ticker.ETH_USD}

    mocker.patch(
        "application.use_cases.price_poll.time.time",
        return_value=float(timestamp),
    )

    async def get_currency_price(ticker: Ticker) -> Decimal:
        if ticker == Ticker.BTC_USD:
            raise RuntimeError("Deribit unavailable")

        return Decimal("3800.123")

    repo_mock.add_records = mocker.AsyncMock()
    latest_price_cache_mock.set_latest_price = mocker.AsyncMock()
    api_client_mock.get_currency_price = mocker.AsyncMock()
    api_client_mock.get_currency_price.side_effect = get_currency_price

    use_case = PricePollUseCase(
        repo=repo_mock,
        cache=latest_price_cache_mock,
        api_client=api_client_mock,
        supported_tickets=supported_tickers,
    )

    await use_case.execute()

    assert api_client_mock.get_currency_price.await_count == 2

    repo_mock.add_records.assert_awaited_once_with(
        [
            PriceRecordDTO(
                ticker=Ticker.ETH_USD, price=Decimal("3800.123"), timestamp=timestamp
            )
        ]
    )
    latest_price_cache_mock.set_latest_price.assert_awaited_once_with(
        PriceRecordDTO(
            ticker=Ticker.ETH_USD, price=Decimal("3800.123"), timestamp=timestamp
        )
    )
