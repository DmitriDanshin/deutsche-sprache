from app.base import AppABC
from parser.context_reverso import ContextReversoParser
from parser.synonyms_reverso import SynonymsReversoParser
from parser.verbformen import VerbformenParser
from utils.distributor import Distributor


class App(AppABC):
    def __init__(
            self,
            query: str
    ):
        query = {
            "w": query
        }

        self.__verbformen_data = (
            VerbformenParser(query=query)
            .parse()
        )

        self.__context_reverso_data = (
            ContextReversoParser(query=query)
            .parse()
        )

        self.__context_synonyms_data = (
            SynonymsReversoParser(query=query)
            .parse()
        )

    def run(self) -> None:
        print(
            Distributor
            .distribute(
                self.__verbformen_data,
                self.__context_reverso_data,
                self.__context_synonyms_data
            )
        )
