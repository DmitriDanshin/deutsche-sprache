from abc import ABC, abstractmethod


class APIHandlerABC(ABC):
    @abstractmethod
    def get(self, query: dict[str, str]) -> str:
        """
        Make an HTTP request
        :returns: clear HTML
        """
        pass


class SoupParserABC(ABC):
    html: str

    @abstractmethod
    def parse(self) -> dict:
        """
        Parse a bs4 object to dict
        :returns: parsed dict
        """
        pass
