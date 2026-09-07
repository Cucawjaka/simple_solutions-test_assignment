import pytest
from pytest_mock import MockerFixture

from application.dto.price_record import PriceRecordDTO
from application.interfaces.latest_price_cache import ILatestPriceCache
from application.interfaces.price_record_repository import IPriceRecordRepository
from application.use_cases.get_latest_ticker_price import GetLatestTickerPriceUseCase
from domain.tickers import Ticker
from errors.application import PriceRecordsNotFoundError


async def test_returns_latest_price_from_cache(
    mocker: MockerFixture,
    repo_mock: IPriceRecordRepository,
    latest_price_cache_mock: ILatestPriceCache,
    price_record: PriceRecordDTO,
) -> None:
    latest_price_cache_mock.get_latest_price = mocker.AsyncMock()
    latest_price_cache_mock.get_latest_price.return_value = price_record
    repo_mock.get_latest_price = mocker.AsyncMock()

    use_case = GetLatestTickerPriceUseCase(
        repo=repo_mock, cache=latest_price_cache_mock
    )

    result = await use_case.execute(ticker=Ticker.BTC_USD)

    assert result == price_record
    latest_price_cache_mock.get_latest_price.assert_awaited_once_with(Ticker.BTC_USD)
    repo_mock.get_latest_price.assert_not_called()


async def test_returns_latest_price_from_repository_on_cache_miss(
    mocker: MockerFixture,
    repo_mock: IPriceRecordRepository,
    latest_price_cache_mock: ILatestPriceCache,
    price_record: PriceRecordDTO,
) -> None:
    latest_price_cache_mock.get_latest_price = mocker.AsyncMock()
    latest_price_cache_mock.get_latest_price.return_value = None
    latest_price_cache_mock.set_latest_price = mocker.AsyncMock()
    repo_mock.get_latest_price = mocker.AsyncMock()
    repo_mock.get_latest_price.return_value = price_record

    use_case = GetLatestTickerPriceUseCase(
        repo=repo_mock, cache=latest_price_cache_mock
    )

    result = await use_case.execute(ticker=Ticker.BTC_USD)

    assert result == price_record
    latest_price_cache_mock.get_latest_price.assert_awaited_once_with(Ticker.BTC_USD)
    repo_mock.get_latest_price.assert_awaited_once_with(Ticker.BTC_USD)
    latest_price_cache_mock.set_latest_price.assert_awaited_once_with(price_record)


async def test_raises_error_when_price_not_found(
    mocker: MockerFixture,
    repo_mock: IPriceRecordRepository,
    latest_price_cache_mock: ILatestPriceCache,
) -> None:
    latest_price_cache_mock.get_latest_price = mocker.AsyncMock()
    latest_price_cache_mock.get_latest_price.return_value = None
    repo_mock.get_latest_price = mocker.AsyncMock()
    repo_mock.get_latest_price.return_value = None

    use_case = GetLatestTickerPriceUseCase(
        repo=repo_mock, cache=latest_price_cache_mock
    )

    with pytest.raises(PriceRecordsNotFoundError) as exc_info:
        await use_case.execute(ticker=Ticker.BTC_USD)

    assert exc_info.value.msg == "Записи по тикету не найдены"
    latest_price_cache_mock.get_latest_price.assert_awaited_once_with(Ticker.BTC_USD)
    repo_mock.get_latest_price.assert_awaited_once_with(Ticker.BTC_USD)
