from abc import ABC, abstractmethod

from bs4 import BeautifulSoup


class HTMLParserABC(ABC):
    @abstractmethod
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        :param html: An HTML text page in UTF-8 encoding
        :return: bs4 object
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
