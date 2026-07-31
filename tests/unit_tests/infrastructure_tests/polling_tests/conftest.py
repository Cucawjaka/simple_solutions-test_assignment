import httpx
import pytest
from pytest_mock import MockerFixture, MockType

from infrastructure.polling.client import DeribitAPIClient


@pytest.fixture
def http_client_mock(mocker: MockerFixture) -> MockType:
    return mocker.Mock(spec=httpx.AsyncClient)


@pytest.fixture
def response_mock(mocker: MockerFixture) -> MockType:
    return mocker.Mock(spec=httpx.Response)


@pytest.fixture
def deribit_client(
    mocker: MockerFixture,
    http_client_mock: httpx.AsyncClient,
    response_mock: httpx.Response,
) -> DeribitAPIClient:
    http_client_mock.get = mocker.AsyncMock()
    http_client_mock.get.return_value = response_mock

    return DeribitAPIClient(client=http_client_mock)
