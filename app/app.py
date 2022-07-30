from app.base import AppABC
from parser.verbformen import VerbformenParser


class App(AppABC):
    def __init__(self, verbformen_query):
        self.__verbformen_data = (
            VerbformenParser(query=verbformen_query)
            .parse()
        )

    def run(self) -> None:
        print(self.__verbformen_data)
