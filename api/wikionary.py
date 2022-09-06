from starlette.datastructures import URL

from api.base import APIHandlerABC
from settings import VERBFORMEN_URL, WIKIONARY_URL

import requests

from utils.logger import wikionary_logger


class WikionaryAPI(APIHandlerABC):
    @classmethod
    def get(cls, query: dict[str, str] | None = None, url: str = WIKIONARY_URL) -> tuple[str, URL]:
        if query is None:
            query = {}
        url = URL(url.format(query["lang"], query['w']))
        response = requests.get(str(url))

        wikionary_logger.info(
            f"Successfully make a GET request to {url} "
            f"with status code {response.status_code}"
        )

        return response.text, url
