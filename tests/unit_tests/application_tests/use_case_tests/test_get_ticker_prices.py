from pytest_mock import MockerFixture

from application.dto.price_record import PriceRecordDTO
from application.interfaces.price_record_repository import IPriceRecordRepository
from application.use_cases.get_ticker_prices import GetTickerPricesUseCase
from domain.tickers import Ticker


async def test_returns_prices(
    mocker: MockerFixture,
    repo_mock: IPriceRecordRepository,
    price_record: PriceRecordDTO,
) -> None:
    expected_records = [price_record]

    repo_mock.get_all = mocker.AsyncMock()
    repo_mock.get_all.return_value = expected_records

    use_case = GetTickerPricesUseCase(repo=repo_mock)

    result = await use_case.execute(ticker=Ticker.BTC_USD, limit=100, offset=0)

    assert result == expected_records


async def test_passes_timestamp_filters_to_repository(
    mocker: MockerFixture,
    repo_mock: IPriceRecordRepository,
    price_record: PriceRecordDTO,
) -> None:
    repo_mock.get_all = mocker.AsyncMock()
    repo_mock.get_all.return_value = [price_record]

    use_case = GetTickerPricesUseCase(repo=repo_mock)

    result = await use_case.execute(
        ticker=Ticker.BTC_USD,
        limit=20,
        offset=10,
        from_timestamp=1000,
        to_timestamp=2000,
    )

    assert result == [price_record]
