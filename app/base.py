from abc import ABC, abstractmethod


class AppABC(ABC):
    @abstractmethod
    def run(self) -> None:
        """
        start an application
        :return: None
        """
        pass
