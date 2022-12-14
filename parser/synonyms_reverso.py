import os.path

from api.synonyms_reverso import SynonymsReversoAPI
from db.mongo import context_synonyms_col
from parser.base import SoupParserABC
from parser.soup import HTMLParser
from utils.errors import Error
from utils.logger import synonyms_reverso_logger, mongodb_logger


class SynonymsReversoParser(SoupParserABC):
    def __init__(self, query: dict[str, str]):
        self.__query_word = query["w"]
        self.__cached_word = (
            context_synonyms_col
            .find_one({"Query": self.__query_word})
        )
        if not self.__cached_word:
            self.__text, self.url, self.status_code = SynonymsReversoAPI.get(query=query)

            self.__soup = (
                HTMLParser
                .parse_html(
                    self.__text
                )
            )

            synonyms_reverso_logger.info(
                f"Successfully tokenized an HTML page"
            )

    @property
    def html(self) -> str:
        """
        Get a prettified HTML
        :return: a prettified HTML
        """
        return self.__soup.prettify()

    def __get_word_synonyms(self) -> list[str]:
        """
        Get the word synonyms (German)
        :return: A list of synonyms
        """

        return [
            word.text for word in
            self.__soup.find_all(
                name="a",
                attrs={"class": "synonym"}
            )
        ]

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
                    f"from '{context_synonyms_col.name}' database"
                )
            else:
                word |= {
                    "Query": self.__query_word,
                    "Synonyms": self.__get_word_synonyms(),
                    "url": str(self.url)
                }
                synonyms_reverso_logger.info(
                    f"Successfully parsed an HTML to dict-like format"
                )
                inserted_word = context_synonyms_col.insert_one(word)
                mongodb_logger.info(
                    f"Successfully insert word {self.__query_word} "
                    f"with id={inserted_word.inserted_id} "
                    f"into '{context_synonyms_col.name}' database"
                )

        except Exception as e:
            synonyms_reverso_logger.error(
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
