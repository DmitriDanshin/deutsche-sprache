import os.path

from api.context_reverso import ContextReversoAPI
from db.mongo import context_reverso_col
from parser.base import SoupParserABC
from parser.soup import HTMLParser
from utils.errors import Error
from utils.logger import context_reverso_logger, mongodb_logger


class ContextReversoParser(SoupParserABC):
    def __init__(self, query: dict[str, str]):
        self.__query_word, self.articleless_word = query["w"], query["w"]
        self.__cached_word = (
            context_reverso_col
            .find_one({"Query": self.__query_word})
        )
        if not self.__cached_word:
            if self.__query_word.startswith(("der", "das", "die")):
                self.articleless_word = self.__query_word[3:].strip()

            self.__text, self.url, self.status_code = (
                ContextReversoAPI.get(query={"w": self.articleless_word})
            )

            self.__soup = (
                HTMLParser
                .parse_html(
                    self.__text
                )
            )

            context_reverso_logger.info(
                f"Successfully tokenized an HTML page"
            )

    @property
    def html(self) -> str:
        """
        Get a prettified HTML
        :return: a prettified HTML
        """
        return self.__soup.prettify()

    def __get_word_examples(self) -> dict[str, str]:
        """
        Get an examples of the word

        For example:

        Hund ->
        {
           "Der Hund hat nicht mit dir gesprochen.":"Нет, Джон, собака не разговаривало с тобой.",
           "Nein, der Hund freut sich.":"Нет, нет! Собаке нравится, когда ты рядом."
            <...>
        }

        :return: a dict where keys are the German sentences and values are translations to Russian language
        """
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
        word = {
            "error": {}
        }

        try:
            if self.__cached_word:
                del self.__cached_word['_id']
                word |= dict(self.__cached_word)
                mongodb_logger.info(
                    f"Successfully loaded cached version for {word['Query']} "
                    f"from '{context_reverso_col.name}' database"
                )
            else:
                word |= {
                    "Query": self.__query_word,
                    "Translations": self.__get_word_translations_rus(),
                    "Examples": self.__get_word_examples(),
                    "url": str(self.url)
                }
                context_reverso_logger.info(
                    f"Successfully parsed an HTML to dict-like format"
                )
                inserted_word = context_reverso_col.insert_one(word)
                mongodb_logger.info(
                    f"Successfully insert word {self.__query_word} "
                    f"with id={inserted_word.inserted_id} "
                    f"into '{context_reverso_col.name}' database"
                )

        except Exception as e:
            context_reverso_logger.error(
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
