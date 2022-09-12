import os.path
from collections import defaultdict

from bs4 import Tag

from api.verbformen import VerbformenAPI
from db.mongo import verbformen_col
from enums.verbformen import SpeechPart
from parser.base import SoupParserABC
from parser.soup import HTMLParser
from settings import (
    VERBFORMEN_WORD_CLASSES, VERBFORMEN_TRANSLATIONS_CLASSES,
    VERBFORMEN_WORD_VERB_CLASSES, VERBFORMEN_NAV_CLASS, AMOUNT_OF_GRAMMATICAL_CASES, NOUNS_WRAPPER_CLASS,
    NOUNS_TABLE_CLASS, STRONG_DECLENSION_INDEX, WEAK_DECLENSION_INDEX,
    MIXED_DECLENSION_INDEX, DECLENSION_TABLE_CLASS,
    VERBS_TABLE_CLASS, VERBS_CELL_CLASS
)
from utils.errors import Error
from utils.logger import verbformen_logger, mongodb_logger


class VerbformenParser(SoupParserABC):
    def __init__(self, query: dict[str, str]):
        self.__query_word = query["w"]
        self.__cached_word = (
            verbformen_col
            .find_one({"Query": self.__query_word})
        )

        if not self.__cached_word:
            self.__text, self.url, self.status_code = VerbformenAPI.get(query=query)
            self.__soup = (
                HTMLParser
                .parse_html(
                    self.__text
                )
            )
            self.__part_of_speech = self.__get_part_of_speech()
            verbformen_logger.info(
                f"Successfully tokenized an HTML page"
            )

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

        word = (
            self
            .__soup
            .find("p", {"class": css_class})
        )

        return word.text.strip()

    def __get_word_translations_rus(self) -> list[str]:

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
        """
           Get a German grammatical conjugation for given word

           For Example:
                  machen:{
                     "Презенс":[
                        "ich mach(e)⁵",
                        <...>
                     ],
                     "Претеритум":[
                        "ich machte",
                        <...>
                     ],
                     "Императив":[
                        "-",
                         <...>
                     ],
                     "Конъюнктив I":[
                        "ich mache",
                         <...>
                     ],
                     "Конъюнктив II":[
                        "ich machte",
                        <...>
                     ],
                     "Инфинитив":[
                        "",
                        <...>
                     ],
                     "Партицип":[
                        "",
                        <...>
                     ]
                  }
               }
            }

           :return: A dict with grammatical conjugation for given word
           """

        forms = defaultdict(list)

        table = (
            self
            .__soup
            .find_all("div", {"class": VERBS_TABLE_CLASS})[1]
        )
        cells = table.find_all("div", {"class": VERBS_CELL_CLASS})
        for cell in cells:
            title = cell.h2
            for row in cell.table:
                forms[title.text].append(row.text.strip())
        return dict(forms)

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

        word = {
            "error": {}
        }

        try:
            if self.__cached_word:
                del self.__cached_word['_id']
                word |= dict(self.__cached_word)
                mongodb_logger.info(
                    f"Successfully loaded cached version for {word['Query']}"
                    f"from '{verbformen_col.name}' database"
                )
            else:
                word |= {
                    "Query": self.__query_word,
                    "Word": self.__get_word(),
                    "PartOfSpeech": self.__get_part_of_speech().value,
                    "Russian": self.__get_word_translations_rus(),
                    "English": self.__get_word_translations_eng(),
                    "Forms": self.__get_word_forms(),
                    "url": str(self.url)
                }
                verbformen_logger.info(
                    f"Successfully parsed an HTML to dict-like format"
                )
                inserted_word = verbformen_col.insert_one(word)
                mongodb_logger.info(
                    f"Successfully insert word {self.__query_word} "
                    f"with id={inserted_word.inserted_id} "
                    f"into '{verbformen_col.name}' database"
                )

        except Exception as e:
            verbformen_logger.error(
                f"An error ({e}) occurred while parsing an HTML to dict-like format"
            )
            error = Error(
                msg=f"Failed to parse a page",
                exception=str(e),
                module=os.path.basename(__name__),
                url=str(self.url),
                status_code=self.status_code
            )

            word["error"] = error.json()

        return word
