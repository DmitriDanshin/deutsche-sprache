from app.base import AppABC
from parser.context_reverso import ContextReversoParser
from parser.verbformen import VerbformenParser


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

    def run(self) -> None:
        print({
            "verbformen": self.__verbformen_data,
            "context_reverso": self.__context_reverso_data
        })
