from abc import ABC, abstractmethod
from typing import List

from scraper.domain.rentals.entities import Rental


class ScrapingService(ABC):
    @abstractmethod
    def scrape_for_rentals(self) -> List[Rental]:
        """Scrape for rentals."""
