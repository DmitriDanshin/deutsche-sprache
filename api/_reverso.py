from starlette.datastructures import URL

from api.base import APIHandlerABC

import requests

from settings import USER_AGENT


class ReversoAPI(APIHandlerABC):
    @classmethod
    def get(cls, query: dict[str, str] | None = None, url: str = "") -> tuple[str, URL, int]:
        headers = {
            'User-Agent': USER_AGENT,
        }
        if query is None:
            query = {}
        url = URL(url.format(query['w']).replace(" ", "+"))
        response = requests.get(str(url), headers=headers)
        status_code = response.status_code
        return response.text, url, status_code
