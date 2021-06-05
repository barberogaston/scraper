from abc import ABC, abstractmethod
from typing import List, Union

from scraper.domain.rentals.entities import Rental


class Repository(ABC):
    @abstractmethod
    def save(self, rentals: Union[Rental, List[Rental]]) -> None:
        """Saves the rental(s)."""

    @abstractmethod
    def truncate(self) -> None:
        """Deletes all the data."""
