from scraper.interfaces.persistence.rentals import RentalsRepository
from scraper.domain.rentals.services import RentalsService
from scraper.infrastructure.db.mysql import MySQLClient, MySQLConnectionData
from scraper.infrastructure.scrapers.services import SeleniumScraper


if __name__ == '__main__':
    conn_data = MySQLConnectionData('root',
                                    'rootpass',
                                    '127.0.0.1',
                                    3306,
                                    'scraper')
    mysql = MySQLClient(conn_data)
    repo = RentalsRepository(mysql)
    scraper = SeleniumScraper()
    service = RentalsService(repo, scraper)
    service.update_rentals()
