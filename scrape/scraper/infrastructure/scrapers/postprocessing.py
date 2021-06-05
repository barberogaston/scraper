import os
import json

import pandas as pd
from scipy import stats

from scraper.infrastructure.scrapers.config import SCRAPER_PATH
from scraper.domain.rentals.entities import Rental, Apartment


def postprocess(data: pd.DataFrame) -> pd.DataFrame:
    return (data.pipe(drop_nan_prices)
                .pipe(drop_duplicates)
                .pipe(add_has_balcony)
                .pipe(add_has_terrace)
                .pipe(add_has_garage)
                .pipe(add_is_studio_apartment)
                .pipe(capitalize_location)
                .pipe(adjust_datatypes)
                .pipe(jsonify_extras))


def has_keywords(row, keywords):
    match = False
    row = row.fillna('')
    for keyword in keywords:
        match = (keyword in row['title'].lower() or
                 keyword in row['description'].lower() or
                 keyword in row['location'].lower() or
                 keyword in row['link'].lower().split('-') or
                 keyword in [e.lower().strip() for e in row['extras']])
        if match:
            break
    return match


def drop_nan_prices(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    return data.dropna(subset=['price'])


def drop_duplicates(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    return data.drop_duplicates('location')


def add_has_balcony(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data.loc[:, 'has_balcony'] = data.apply(has_keywords,
                                            args=(['balcón',
                                                   'balcon',
                                                   'balcones'],),
                                            axis=1)
    return data


def add_has_terrace(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data.loc[:, 'has_terrace'] = data.apply(has_keywords,
                                            args=(['terraza', 'terrazas'],),
                                            axis=1)
    return data


def add_is_studio_apartment(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data.loc[:, 'is_studio_apartment'] = data.apply(has_keywords,
                                                    args=(['monoambiente',
                                                           'monoambientes'],),
                                                    axis=1)
    return data


def add_has_garage(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data.loc[:, 'has_garage'] = data.apply(has_keywords,
                                           args=(['cochera', 'cocheras'],),
                                           axis=1)
    return data


def capitalize_location(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data.loc[:, 'location'] = data.loc[:, 'location'].str.capitalize()
    return data


def adjust_datatypes(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    dtypes = {'price': float,
              'expenses': float,
              'has_balcony': float,
              'has_terrace': float,
              'is_studio_apartment': float,
              'rooms': float}
    return data.astype(dtypes)


def remove_expenses_outliers(data: pd.DataFrame) -> pd.DataFrame:
    expenses = data['expenses'].copy()
    transform = stats.boxcox(expenses, -0.2)
    z = (transform - transform.mean()) / transform.std()
    return data[(-5 <= z) & (z <= 5)].copy()


def remove_price_outliers(data: pd.DataFrame) -> pd.DataFrame:
    price = data['price'].copy()
    transform = stats.boxcox(price, -2)
    z = (transform - transform.mean()) / transform.std()
    return data[(-5 <= z) & (z <= 5)].copy()


def jsonify_extras(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data.loc[:, 'extras'] = data['extras'].apply(json.dumps)
    return data


def unmarshal_row(row: dict) -> Rental:
    apartment = Apartment(row['location'],
                          row['total_surface'],
                          row['covered_surface'],
                          row['has_balcony'],
                          row['has_terrace'],
                          row['has_garage'],
                          row['is_studio_apartment'],
                          row['rooms'],
                          row['extras'])
    rental = Rental(row['title'],
                    row['description'],
                    row['price'],
                    row['expenses'],
                    row['link'],
                    apartment)
    return rental
