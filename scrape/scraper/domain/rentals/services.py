from scraper.domain.rentals.repositories import Repository
from scraper.domain.scraping.services import ScrapingService


class RentalsService:
    def __init__(
        self,
        repository: Repository,
        scraping_service: ScrapingService
    ) -> None:
        self._repository = repository
        self._scraping_service = scraping_service

    def update_rentals(self) -> None:
        """Scrape for rentals and update the repository."""
        rentals = self._scraping_service.scrape_for_rentals()
        self._repository.truncate()
        self._repository.save(rentals)
