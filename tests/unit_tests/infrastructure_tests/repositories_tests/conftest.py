from decimal import Decimal

import pytest
from pytest_mock import MockerFixture, MockType
from sqlalchemy.ext.asyncio import AsyncSession

from application.dto.price_record import PriceRecordDTO
from domain.tickers import Ticker
from infrastructure.db.models import PriceRecordModel
from infrastructure.repositories.price_record import PriceRecordRepository


@pytest.fixture
def session_mock(mocker: MockerFixture) -> MockType:
    return mocker.Mock(spec=AsyncSession)


@pytest.fixture
def repository(session_mock: AsyncSession) -> PriceRecordRepository:
    return PriceRecordRepository(session=session_mock)


@pytest.fixture
def price_records() -> list[PriceRecordDTO]:
    return [
        PriceRecordDTO(
            ticker=Ticker.BTC_USD, price=Decimal("118500.123"), timestamp=1_722_424_800
        ),
        PriceRecordDTO(
            ticker=Ticker.ETH_USD, price=Decimal("3800.123"), timestamp=1_722_424_800
        ),
    ]


@pytest.fixture
def price_model_mock(mocker: MockerFixture) -> PriceRecordModel:
    model = mocker.Mock(spec=PriceRecordModel)
    model.price = Decimal("118500.123")
    model.timestamp = 1_722_424_800

    return model
