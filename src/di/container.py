from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from di.providers.use_case import UseCasesProvider


def create_container() -> AsyncContainer:
    """Создает IoC контейнер."""
    return make_async_container(UseCasesProvider(), FastapiProvider())
