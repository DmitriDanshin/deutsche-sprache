from bs4 import Tag

from api.verbformen import VerbformenAPI
from api.base import SoupParserABC
from enums.verbformen import SpeechPart
from parser.soup import HTMLParser
from settings import (
    VERBFORMEN_WORD_CLASSES, VERBFORMEN_TRANSLATIONS_CLASSES,
    VERBFORMEN_WORD_VERB_CLASSES, VERBFORMEN_NAV_CLASS, AMOUNT_OF_GRAMMATICAL_CASES, NOUNS_WRAPPER_CLASS,
    NOUNS_TABLE_CLASS, STRONG_DECLENSION_INDEX, WEAK_DECLENSION_INDEX, MIXED_DECLENSION_INDEX, DECLENSION_TABLE_CLASS
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
        return (
            self
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

        return (
            self
            .__soup
            .find("dd", {"lang": "en"})
            .text.strip()
            .split(", ")
        )

    def __get_verb_forms(self) -> dict:
        return {}

    def __get_noun_forms(self) -> dict[str, dict[str, str]]:
        """
        Get a German grammatical cases for given word

        For Example:
        der Hund:
        "forms":{
         "Единственное число":{
            "Им.":"der Hund",
            "Pод.":"des Hundes/Hunds",
            "Дат.":"dem Hund/Hunde⁶",
            "Вин.":"den Hund"
         },
         "Множественное число":{
            "Им.":"die Hunde",
            "Pод.":"der Hunde",
            "Дат.":"den Hunden",
            "Вин.":"die Hunde"
         }
        }

        :return: A dict with grammatical cases for given word
        """
        noun_forms = {
            "Единственное число": {},
            "Множественное число": {}
        }

        table = (
            self
            .__soup
            .find("div", {
                "class": NOUNS_WRAPPER_CLASS
            })
            .find_all("div", {
                "class": NOUNS_TABLE_CLASS
            })
        )

        for element in table:
            grammatical_number = element.h2
            for case_index in range(AMOUNT_OF_GRAMMATICAL_CASES):
                case = element.find_all("tr")[case_index].th
                article = element.find_all("tr")[case_index].find_all('td')[0]
                word = element.find_all("tr")[case_index].find_all('td')[1]
                noun_forms[grammatical_number.text][case.text] = (
                    f"{article.text} {word.text}"
                )

        return noun_forms

    @staticmethod
    def __get_declension(section: Tag, declension: dict, declension_type: str):
        for element in section.find_all("div", {"class": DECLENSION_TABLE_CLASS}):
            title = element.h3
            for word in element.find_all('tr'):
                case = word.find('th')
                article = word.find_all("td")[0]
                word = word.find_all("td")[1]
                declension[declension_type][title.text][case.text] = (
                    f"{article.text} {word.text}"
                )
        return declension

    @staticmethod
    def __get_strong_declension(sections: list):
        strong_declension = {
            "Сильное склонение": {
                "Mужской род": {},
                "Женский род": {},
                "Средний род": {},
                "Множественное число": {}
            }
        }
        section = sections[STRONG_DECLENSION_INDEX]

        for element in section.find_all("div", {"class": DECLENSION_TABLE_CLASS}):
            title = element.h2
            for case, word in zip(element.find_all("th"), element.find_all('td')):
                strong_declension['Сильное склонение'][title.text][case.text] = (
                    word.text
                )

        return strong_declension

    def __get_weak_declension(self, sections: list):
        weak_declension = {
            "Слабое склонение": {
                "Mужской род": {},
                "Женский род": {},
                "Средний род": {},
                "Множественное число": {}
            },
        }
        section = sections[WEAK_DECLENSION_INDEX]

        return self.__get_declension(
            section,
            weak_declension,
            "Слабое склонение"
        )

    def __get_mixed_declension(self, sections: list):
        mixed_declension = {
            "Смешанное склонение": {
                "Mужской род": {},
                "Женский род": {},
                "Средний род": {},
                "Множественное число": {}
            },
        }

        section = sections[MIXED_DECLENSION_INDEX]

        return self.__get_declension(
            section,
            mixed_declension,
            "Смешанное склонение"
        )

    def __get_adjective_forms(self) -> dict:
        sections = self.__soup.find_all("section", {"class": "rBox rBoxWht"})
        adjective_forms = {
            **self.__get_strong_declension(sections),
            **self.__get_weak_declension(sections),
            **self.__get_mixed_declension(sections)
        }

        return adjective_forms

    def __get_word_forms(self):
        forms: dict
        match self.__part_of_speech:
            case SpeechPart.VERB:
                forms = self.__get_verb_forms()
            case SpeechPart.NOUN:
                forms = self.__get_noun_forms()
            case SpeechPart.ADJECTIVE:
                forms = self.__get_adjective_forms()
            case _:
                forms = {}
        return forms

    def parse(self) -> dict:
        """
        Transform the entire HTML page to dict-like format

        :return: dict-like object
        """

        return {
            self.__get_word(): {
                "Часть речи": self.__get_part_of_speech().value,
                "Переводы на русский": self.__get_word_translations_rus(),
                "Переводы на английский": self.__get_word_translations_eng(),
                "Формы": self.__get_word_forms()
            }
        }
