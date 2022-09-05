from abc import ABC, abstractmethod


class APIHandlerABC(ABC):
    @abstractmethod
    def get(self, query: dict[str, str]) -> str:
        """
        Make an HTTP request
        :returns: clear HTML
        """
        pass


