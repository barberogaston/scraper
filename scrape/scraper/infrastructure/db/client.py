from abc import ABC, abstractmethod


class DatabaseClient(ABC):
    @abstractmethod
    def execute(self, query: str) -> None:
        """Executes a query with no result."""
