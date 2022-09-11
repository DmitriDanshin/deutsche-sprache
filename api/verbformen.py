from starlette.datastructures import URL

from api.base import APIHandlerABC
from settings import VERBFORMEN_URL

import requests

from utils.logger import verbformen_logger


class VerbformenAPI(APIHandlerABC):
    @classmethod
    def get(cls, query: dict[str, str] | None = None) -> tuple[str, URL, int]:
        if query is None:
            query = {}
        url = URL(VERBFORMEN_URL)
        url = url.include_query_params(**query)

        response = requests.get(str(url))

        status_code = response.status_code
        verbformen_logger.info(
            f"Successfully make a GET request to {VERBFORMEN_URL} "
            f"with status code {status_code}"
        )

        return response.text, url, status_code
