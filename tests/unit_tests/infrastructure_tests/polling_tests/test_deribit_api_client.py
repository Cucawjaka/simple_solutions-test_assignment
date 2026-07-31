import json
from decimal import Decimal

import httpx
import pytest
from pytest_mock import MockerFixture

from domain.tickers import Ticker
from errors.application import IntegrationError
from infrastructure.polling.client import DeribitAPIClient


async def test_returns_currency_price(
    mocker: MockerFixture,
    deribit_client: DeribitAPIClient,
    http_client_mock: httpx.AsyncClient,
    response_mock: httpx.Response,
) -> None:
    response_mock.json = mocker.Mock()
    response_mock.json.return_value = {"result": {"index_price": 118500.123}}

    result = await deribit_client.get_currency_price(Ticker.BTC_USD)

    assert result == Decimal("118500.123")


async def test_raises_integration_error_on_http_error(
    mocker: MockerFixture,
    deribit_client: DeribitAPIClient,
    http_client_mock: httpx.AsyncClient,
) -> None:
    http_client_mock.get = mocker.AsyncMock()
    http_client_mock.get.side_effect = httpx.RequestError("Connection failed")

    with pytest.raises(IntegrationError):
        await deribit_client.get_currency_price(Ticker.BTC_USD)


async def test_raises_integration_error_on_invalid_json(
    mocker: MockerFixture,
    deribit_client: DeribitAPIClient,
    response_mock: httpx.Response,
) -> None:
    response_mock.json = mocker.Mock()
    response_mock.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

    with pytest.raises(IntegrationError):
        await deribit_client.get_currency_price(Ticker.BTC_USD)


async def test_raises_integration_error_when_api_returns_error(
    mocker: MockerFixture,
    deribit_client: DeribitAPIClient,
    response_mock: httpx.Response,
) -> None:
    response_mock.json = mocker.Mock()
    response_mock.json.return_value = {
        "error": {"message": "Invalid params", "code": 10000, "data": {}}
    }

    with pytest.raises(IntegrationError):
        await deribit_client.get_currency_price(Ticker.BTC_USD)
