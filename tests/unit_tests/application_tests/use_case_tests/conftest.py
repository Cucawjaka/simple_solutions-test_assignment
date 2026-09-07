from decimal import Decimal

import pytest
from pytest_mock import MockerFixture, MockType

from application.dto.price_record import PriceRecordDTO
from application.interfaces.deribit_client import IDeribitAPIClient
from application.interfaces.latest_price_cache import ILatestPriceCache
from application.interfaces.price_record_repository import IPriceRecordRepository
from domain.tickers import Ticker


@pytest.fixture
def repo_mock(mocker: MockerFixture) -> MockType:
    return mocker.Mock(spec=IPriceRecordRepository)


@pytest.fixture
def api_client_mock(mocker: MockerFixture) -> MockType:
    return mocker.Mock(spec=IDeribitAPIClient)


@pytest.fixture
def latest_price_cache_mock(mocker: MockerFixture) -> MockType:
    return mocker.Mock(spec=ILatestPriceCache)


@pytest.fixture
def price_record() -> PriceRecordDTO:
    return PriceRecordDTO(
        ticker=Ticker.BTC_USD, price=Decimal("118500.123"), timestamp=1_722_424_800
    )


@pytest.fixture
def supported_tickers() -> set[Ticker]:
    return {Ticker.BTC_USD}
