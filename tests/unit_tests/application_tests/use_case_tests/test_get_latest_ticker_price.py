import pytest
from pytest_mock import MockerFixture

from application.dto.price_record import PriceRecordDTO
from application.interfaces.price_record_repository import IPriceRecordRepository
from application.use_cases.get_latest_ticker_price import GetLatestTickerPriceUseCase
from domain.tickers import Ticker
from errors.application import PriceRecordsNotFoundError


async def test_returns_latest_price(
    mocker: MockerFixture,
    repo_mock: IPriceRecordRepository,
    price_record: PriceRecordDTO,
) -> None:
    repo_mock.get_latest_price = mocker.AsyncMock()
    repo_mock.get_latest_price.return_value = price_record

    use_case = GetLatestTickerPriceUseCase(repo=repo_mock)

    result = await use_case.execute(ticker=Ticker.BTC_USD)

    assert result == price_record
    repo_mock.get_latest_price.assert_awaited_once_with(Ticker.BTC_USD)


async def test_raises_error_when_price_not_found(
    mocker: MockerFixture, repo_mock: IPriceRecordRepository
) -> None:
    repo_mock.get_latest_price = mocker.AsyncMock()
    repo_mock.get_latest_price.return_value = None

    use_case = GetLatestTickerPriceUseCase(repo=repo_mock)

    with pytest.raises(PriceRecordsNotFoundError) as exc_info:
        await use_case.execute(ticker=Ticker.BTC_USD)

    assert exc_info.value.msg == "Записи по тикету не найдены"
    repo_mock.get_latest_price.assert_awaited_once_with(Ticker.BTC_USD)
