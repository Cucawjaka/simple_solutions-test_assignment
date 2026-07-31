from decimal import Decimal

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from application.dto.price_record import PriceRecordDTO
from domain.tickers import Ticker
from errors.application import (
    IntegrationError,
    TickerNotFoundError,
)
from infrastructure.db.models import PriceRecordModel
from infrastructure.repositories.price_record import PriceRecordRepository


async def test_adds_records(
    mocker: MockerFixture,
    repository: PriceRecordRepository,
    session_mock: AsyncSession,
    price_records: list[PriceRecordDTO],
) -> None:
    session_mock.execute = mocker.AsyncMock()
    session_mock.add_all = mocker.AsyncMock()
    session_mock.commit = mocker.AsyncMock()
    session_mock.rollback = mocker.AsyncMock()

    session_mock.execute.return_value = [
        (Ticker.BTC_USD.value, 1),
        (Ticker.ETH_USD.value, 2),
    ]

    await repository.add_records(price_records)

    session_mock.add_all.assert_called_once()
    session_mock.commit.assert_awaited_once_with()
    session_mock.rollback.assert_not_awaited()


async def test_raises_error_when_ticker_not_found(
    mocker: MockerFixture,
    repository: PriceRecordRepository,
    session_mock: AsyncSession,
    price_records: list[PriceRecordDTO],
) -> None:
    session_mock.execute = mocker.AsyncMock()
    session_mock.execute.return_value = [(Ticker.BTC_USD.value, 1)]

    with pytest.raises(TickerNotFoundError):
        await repository.add_records(price_records)


async def test_rolls_back_when_commit_failed(
    mocker: MockerFixture,
    repository: PriceRecordRepository,
    session_mock: AsyncSession,
    price_records: list[PriceRecordDTO],
) -> None:
    session_mock.execute = mocker.AsyncMock()
    session_mock.commit = mocker.AsyncMock()

    session_mock.execute.return_value = [
        (Ticker.BTC_USD.value, 1),
        (Ticker.ETH_USD.value, 2),
    ]
    session_mock.commit.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(IntegrationError):
        await repository.add_records(price_records)


async def test_returns_all_prices(
    mocker: MockerFixture,
    repository: PriceRecordRepository,
    session_mock: AsyncSession,
    price_model_mock: PriceRecordModel,
) -> None:
    scalar_result = mocker.Mock()
    scalar_result.all.return_value = [price_model_mock]

    session_mock.scalars = mocker.AsyncMock()
    session_mock.scalars.return_value = scalar_result

    result = await repository.get_all(ticker=Ticker.BTC_USD, limit=100, offset=0)

    assert result == [
        PriceRecordDTO(
            ticker=Ticker.BTC_USD, price=Decimal("118500.123"), timestamp=1_722_424_800
        )
    ]


async def test_get_all_raises_integration_error(
    mocker: MockerFixture,
    repository: PriceRecordRepository,
    session_mock: AsyncSession,
) -> None:
    session_mock.scalars = mocker.AsyncMock()
    session_mock.scalars.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(IntegrationError):
        await repository.get_all(ticker=Ticker.BTC_USD, limit=100, offset=0)


async def test_returns_latest_price(
    mocker: MockerFixture,
    repository: PriceRecordRepository,
    session_mock: AsyncSession,
    price_model_mock: PriceRecordModel,
) -> None:
    session_mock.scalar = mocker.AsyncMock()
    session_mock.scalar.return_value = price_model_mock

    result = await repository.get_latest_price(Ticker.BTC_USD)

    assert result == PriceRecordDTO(
        ticker=Ticker.BTC_USD, price=Decimal("118500.123"), timestamp=1_722_424_800
    )


async def test_returns_none_when_latest_price_not_found(
    mocker: MockerFixture,
    repository: PriceRecordRepository,
    session_mock: AsyncSession,
) -> None:
    session_mock.scalar = mocker.AsyncMock()
    session_mock.scalar.return_value = None

    result = await repository.get_latest_price(Ticker.BTC_USD)

    assert result is None
    session_mock.scalar.assert_awaited_once()
