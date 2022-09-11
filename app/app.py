from app.base import AppABC
from parser.context_reverso import ContextReversoParser
from parser.verbformen import VerbformenParser


class App(AppABC):
    def __init__(
            self,
            verbformen_query: dict[str, str],
            context_reverso_query: dict[str, str]
    ):
        self.__verbformen_data = (
            VerbformenParser(query=verbformen_query)
            .parse()
        )
        self.__context_reverso_data = (
            ContextReversoParser(query=context_reverso_query)
            .parse()
        )

    def run(self) -> None:
        print({
            "verbformen": self.__verbformen_data,
            "context_reverso": self.__context_reverso_data
        })
