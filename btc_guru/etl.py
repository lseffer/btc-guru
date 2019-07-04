from abc import ABC, abstractmethod
from typing import Any


class ETL(ABC):

    @abstractmethod
    def extract(self) -> Any:
        pass

    @abstractmethod
    def transform(self, data: Any) -> None:
        return data

    @abstractmethod
    def load(self, data: Any) -> None:
        pass

    def job(self) -> None:
        data = self.extract()
        data = self.transform(data)
        self.load(data)
