from collections import defaultdict
from api.wikionary import WikionaryAPI
from parser.base import SoupParserABC
from settings import EXCLUDED
from utils.logger import wikionary_logger
from parser.soup import HTMLParser


class WikionaryParser(SoupParserABC):
    def __init__(self, query: dict[str, str]):
        self.__text, self.url = WikionaryAPI.get(query=query)

        self.__soup = (
            HTMLParser
            .parse_html(
                self.__text
            )
        )
        self.__word = query["w"]

        wikionary_logger.info(
            f"Successfully parsed an HTML page"
        )

    @property
    def html(self) -> str:
        """
        Get a prettified HTML

        :return: a prettified HTML
        """
        return self.__soup.prettify()

    @staticmethod
    def __format_sentence(sentence: str) -> str:
        """
        Get a sentence and return sentence without any special
        symbols e.g. (▼ ≠ ≈) and digits.
        :return: a formatted sentence
        """
        formatted_sentence = ""
        for word in sentence.split(" "):
            for letter in word:
                if letter.isalpha():
                    formatted_sentence += letter
            formatted_sentence += " "

        for exclude in EXCLUDED:
            formatted_sentence = formatted_sentence.replace(exclude, "")

        return formatted_sentence.strip().capitalize()

    def parse(self) -> dict:
        """
        Transform the entire HTML page to dict-like format

        :return: dict-like object
        """
        word_information = defaultdict(list)
        for element in self.__soup.find_all('h4'):
            title = element.find_all("span")[1].text
            for li in element.find_next_sibling():
                if li == "\n":
                    continue
                if text := self.__format_sentence(li.text):
                    word_information[title.strip()].append(text)
        return {
            **word_information,
            "url": str(self.url)
        }
