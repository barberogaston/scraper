from typing import List, Union

from scraper.domain.rentals.entities import Rental
from scraper.domain.rentals.repositories import Repository
from scraper.infrastructure.db.mysql import MySQLClient


class QueryBuilder:
    def make_insert(self, rentals: List[Rental]) -> str:
        columns = self._rentals_to_columns(rentals)
        values = self._rentals_to_values(rentals)
        query = f'INSERT INTO `scraper`.`rentals`{columns} VALUES {values}'
        return query.replace('nan', 'NULL')

    def _rental_to_dict(self, rental: Rental) -> dict:
        apartment_dict = rental.__dict__['apartment'].__dict__
        rental_dict = rental.__dict__
        return {
            k: v for k, v in {**apartment_dict, **rental_dict}.items()
            if k != 'apartment'
        }

    def _rentals_to_values(self, rentals: List[Rental]) -> str:
        values = [str(tuple(self._rental_to_dict(rental).values()))
                  for rental in rentals]
        return ', '.join(values)

    def _rentals_to_columns(self, rentals: List[Rental]) -> str:
        return f"""(
            {','.join(f'`{col}`'
            for col in self._rental_to_dict(rentals[0]).keys())}
        )"""


class RentalsRepository(Repository):
    def __init__(self, client: MySQLClient) -> None:
        self._client = client
        self._query_builder = QueryBuilder()

    def save(self, rentals: Union[Rental, List[Rental]]) -> None:
        """Saves the rental(s)."""
        if not isinstance(rentals, list):
            rentals = [rentals]

        query = self._query_builder.make_insert(rentals)
        self._client.execute(query)

    def truncate(self) -> None:
        """Deletes all the data."""
        self._client.execute('DELETE FROM rentals;')
