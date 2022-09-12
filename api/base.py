from abc import ABC, abstractmethod

from starlette.datastructures import URL


class APIHandlerABC(ABC):
    @abstractmethod
    def get(self, query: dict[str, str]) -> tuple[str, URL, int]:
        """
        Make an HTTP request
        :returns: an HTML, requested url and status code
        """
        pass
