import os.path

from api.context_reverso import ContextReversoAPI
from parser.base import SoupParserABC
from parser.soup import HTMLParser
from utils.logger import reverso_logger


class ContextReversoParser(SoupParserABC):
    def __init__(self, query: dict[str, str]):
        self.__text, self.url = ContextReversoAPI.get(query=query)

        self.__soup = (
            HTMLParser
            .parse_html(
                self.__text
            )
        )
        reverso_logger.info(
            f"Successfully parsed an HTML page"
        )
        self.__word = query["w"]

    @property
    def html(self) -> str:
        """
        Get a prettified HTML
        :return: a prettified HTML
        """
        return self.__soup.prettify()

    def __get_word_examples(self) -> dict[str, str]:
        examples_sections = (
            self
            .__soup
            .find("section", {"id": "examples-content"})
        )
        examples_divs = examples_sections.find_all("div", {"class": "example"})
        examples = {}
        for div in examples_divs:
            sentence = div.find("div", {"class": "src ltr"}).text.strip()
            translation = div.find("div", {"class": "trg ltr"}).text.strip()
            examples[sentence] = translation

        return examples

    def __get_word_translations_rus(self) -> list[str]:
        """
        Get a word's Russian translations from HTML page

        For example: ['пёс', 'собака', 'соба́ка']

        :return: a list of word's translations (rus)
        """

        translations = [
            word.text for word in self.__soup.find_all(
                "span", {"class": "display-term"}
            )
        ]

        return translations

    def parse(self) -> dict:
        """
        Transform the entire HTML page to dict-like format

        :return: dict-like object
        """

        try:
            word = {
                self.__word: {
                    "Переводы": self.__get_word_translations_rus(),
                    "Примеры": self.__get_word_examples(),
                    "url": str(self.url)
                }
            }
            reverso_logger.info(
                f"Successfully parsed an HTML to dict-like format"
            )
        except AttributeError as e:
            reverso_logger.error(
                f"An error ({e}) occurred while parsing an HTML to dict-like format"
            )
            return {
                "error": {
                    "msg": f"Failed to parse a page",
                    "type": e,
                    "module": os.path.basename(__file__),
                    "url": str(self.url)
                },
            }
        return word
