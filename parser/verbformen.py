from api.verbformen import VerbformenAPI
from api.base import SoupParserABC
from enums.verbformen import SpeechPart
from parser.soup import HTMLParser
from settings import (
    VERBFORMEN_WORD_CLASSES, VERBFORMEN_TRANSLATIONS_CLASSES,
    VERBFORMEN_WORD_VERB_CLASSES, VERBFORMEN_NAV_CLASS
)


class VerbformenParser(SoupParserABC):
    def __init__(self, query: dict[str, str]):
        self.__soup = (
            HTMLParser
            .parse_html(
                VerbformenAPI
                .get(query=query)
            )
        )
        self.__part_of_speech = self.__get_part_of_speech()

    @property
    def html(self) -> str:
        """
        Get a prettified HTML
        :return: a prettified HTML
        """
        return self.__soup.prettify()

    def __get_part_of_speech(self) -> SpeechPart:
        nav_items = {
            nav_item.strip() for nav_item in
            self
            .__soup
            .find("nav", VERBFORMEN_NAV_CLASS)
            .text
            .split("›")
        }

        if "Спряжение" in nav_items:
            return SpeechPart.VERB
        elif "Cуществительные" in nav_items:
            return SpeechPart.NOUN
        elif "Прилагательные" in nav_items:
            return SpeechPart.ADJECTIVE

        return SpeechPart.NOUN

    def __get_word(self) -> str:
        """
        Get a German word from HTML page

        For example: der Hund, das Haus

        :return: a word
        """

        match self.__part_of_speech:
            case SpeechPart.VERB:
                css_class = VERBFORMEN_WORD_VERB_CLASSES
            case SpeechPart.NOUN | SpeechPart.ADJECTIVE:
                css_class = VERBFORMEN_WORD_CLASSES
            case _:
                css_class = VERBFORMEN_WORD_CLASSES

        word = (self
                .__soup
                .find("p", {"class": css_class})
                )

        return word.text.strip()

    def __get_word_translations_rus(self) -> list[str]:
        """
        Get a word's Russian translations from HTML page

        For example: ['пёс', 'собака', 'соба́ка']

        :return: a list of word's translations (rus)
        """
        return (self
                .__soup
                .find("p", {"class": VERBFORMEN_TRANSLATIONS_CLASSES})
                .text
                .strip()
                .split(",\n")
                )

    def __get_word_translations_eng(self) -> list[str]:
        """
        Get a word's English translations from HTML page

        For example: ['dog', 'hound']

        :return: a list of word's translations (eng)
        """

        return (self
                .__soup
                .find("dd", {"lang": "en"})
                .text.strip()
                .split(", "))

    def parse(self) -> dict:
        """
        Transform the entire HTML page to dict-like format

        :return: dict-like object
        """

        return {
            self.__get_word(): {
                "part_of_speech": self.__get_part_of_speech().value,
                "translations_rus": self.__get_word_translations_rus(),
                "translations_eng": self.__get_word_translations_eng()
            }
        }
