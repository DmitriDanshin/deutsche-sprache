from starlette.datastructures import URL

from api.base import APIHandlerABC

import requests

from settings import CONTEXT_REVERSO_URL, USER_AGENT
from utils.logger import reverso_logger


class ContextReversoAPI(APIHandlerABC):
    @classmethod
    def get(cls, query: dict[str, str] | None = None) -> tuple[str, URL]:
        headers = {
            'User-Agent': USER_AGENT,
        }
        if query is None:
            query = {}
        url = URL(CONTEXT_REVERSO_URL.format(query['w']).replace(" ", "+"))
        response = requests.get(str(url), headers=headers)

        reverso_logger.info(
            f"Successfully make a GET request to {url} "
            f"with status code {response.status_code}"
        )

        return response.text, url
