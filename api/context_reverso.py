from starlette.datastructures import URL

from api.base import APIHandlerABC
from api._reverso import ReversoAPI
from settings import CONTEXT_REVERSO_URL
from utils.logger import context_reverso_logger


class ContextReversoAPI(APIHandlerABC):
    @classmethod
    def get(cls, query: dict[str, str] | None = None) -> tuple[str, URL, int]:
        text, url, status_code = ReversoAPI.get(query, url=CONTEXT_REVERSO_URL)
        context_reverso_logger.info(
            f"Successfully make a GET request to {url} "
            f"with status code {status_code}"
        )
        return text, url, status_code
