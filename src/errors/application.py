class ApplicationError(Exception):
    """Базовое исключение для ошибок, возникающих в слое приложения."""

    def __init__(self, msg: str) -> None:
        self.msg: str = msg


class IntegrationError(ApplicationError):
    """Исключение, возникающее при ошибках интеграции с внешними сервисами."""


class TickerNotFoundError(ApplicationError):
    """Исключение, возникающее при обращении к несуществующему тикеру."""


class PriceRecordsNotFoundError(ApplicationError):
    """Исключение, вощникающее при отсутствии записей по тикету."""
