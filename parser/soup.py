from bs4 import BeautifulSoup

from parser.base import HTMLParserABC


class HTMLParser(HTMLParserABC):
    @classmethod
    def parse_html(cls, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, 'html.parser')
