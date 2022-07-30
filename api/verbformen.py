from starlette.datastructures import URL

from api.base import APIHandlerABC
from settings import VERBFORMEN_URL

import requests


class VerbformenAPI(APIHandlerABC):
    @classmethod
    def get(cls, query: dict[str, str] | None = None) -> str:
        if query is None:
            query = {}
        url = URL(VERBFORMEN_URL)
        url = url.include_query_params(**query)
        return requests.get(str(url)).text
