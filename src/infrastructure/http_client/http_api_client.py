import logging

from aiohttp import (
    ClientConnectionError,
    ClientSession,
    ClientSSLError,
    ClientTimeout,
)

from src.core.exceptions.external_api import ExternalApiError

logger = logging.getLogger(__name__)


class HttpClientFactory:
    def __init__(self) -> None:
        self.session: ClientSession | None = None

    async def get_session(self) -> ClientSession:
        if self.session is None:
            self.session = ClientSession(
                # base_url=settings.example.base_url,
                timeout=ClientTimeout(total=30),
                headers={
                    # "x-example-api-key": settings.example.token,
                    "Content-Type": "application/json",
                },
            )
            logger.info("HTTP client created")
        return self.session

    async def close(self) -> None:
        if self.session:
            try:
                logger.info("Closing HTTP client")
                await self.session.close()
                logger.info("HTTP client closed")
            except Exception as e:
                logger.error(f"Error closing HTTP client: {e}")
            finally:
                self.session = None


http_factory = HttpClientFactory()


async def get_http_session() -> ClientSession:
    try:
        return await http_factory.get_session()
    except ClientSSLError as e:
        logger.error(f"SSL error: {e}")
        raise ExternalApiError("Failed to create HTTP client: SSL error")
    except ClientConnectionError as e:
        logger.error(f"Connection error: {e}")
        raise ExternalApiError("Failed to create HTTP client: Connection error")
    except Exception as e:
        logger.error(f"Unexpected error creating HTTP client: {e}")
        raise ExternalApiError(f"Failed to create HTTP client: {str(e)}")
