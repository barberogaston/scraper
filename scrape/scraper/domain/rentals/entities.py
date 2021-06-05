from dataclasses import dataclass


@dataclass
class Apartment:
    location: str
    total_surface: int
    covered_surface: int
    has_balcony: bool
    has_terrace: bool
    has_garage: bool
    is_studio_apartment: bool
    rooms: int
    extras: str


@dataclass
class Rental:
    title: str
    description: str
    price: float
    expenses: float
    link: str
    apartment: Apartment
