import sys

import structlog
import uvicorn

from config import WebServerConfig
from di.container import create_container
from infrastructure.web_server.bootstrap import create_app
from logger_config import configure_logging

logger = structlog.getLogger(__name__)


def main() -> None:
    """Точка запуска приложения"""
    configure_logging()

    try:
        web_server_config = WebServerConfig()
    except Exception as e:
        logger.exception("Ошибка при загрузке конфигурации", error=str(e))
        sys.exit(1)
    else:
        container = create_container()

    app = create_app(container=container)

    uvicorn.run(
        app=app,
        host=web_server_config.server_host,
        port=web_server_config.server_port,
    )


if __name__ == "__main__":
    logger.info("Start server!")
    main()
