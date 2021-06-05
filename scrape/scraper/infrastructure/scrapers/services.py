import json
import os
import re
from typing import List, Optional

import pandas as pd
from scraper.domain.rentals.entities import Rental
from scraper.domain.scraping.services import ScrapingService
from scraper.infrastructure.scrapers.config import SCRAPER_PATH
from scraper.infrastructure.scrapers.postprocessing import (postprocess,
                                                            unmarshal_row)
from scraper.infrastructure.scrapers.utils import normalize_html_string
from scraper.infrastructure.scrapers.zonaprop.spiders import ZonapropSpider
from scrapy.crawler import CrawlerProcess
from selenium.webdriver import Chrome


class ScrapyScraper(ScrapingService):
    def __init__(self) -> None:
        self._spider_classes = [ZonapropSpider]

    def scrape_for_rentals(self) -> List[Rental]:
        """Scrape for rentals."""
        self._run_scrapers()
        data = self._read_data()
        data = postprocess(data)
        data = data.to_dict(orient='records')
        return [unmarshal_row(row) for row in data]

    def _run_scrapers(self) -> pd.DataFrame:
        """Run the scraper and return the results as a pandas
        dataframe."""
        process = CrawlerProcess()
        for spider in self._spider_classes:
            process.crawl(spider)
        process.start()
        process.stop()

    def _read_data(self) -> pd.DataFrame:
        files = [
            f'{SCRAPER_PATH}/{file}'
            for file in os.listdir(SCRAPER_PATH) if file.endswith('json')
        ]
        return pd.concat([
            pd.DataFrame.from_records(json.load(open(file, 'r')))
            for file in files
        ])


class SeleniumScraper(ScrapingService):
    def __init__(self):
        self.base_url = 'https://www.zonaprop.com.ar'
        self.endpoint = '/departamentos-alquiler-nueva-cordoba'
        self.driver = Chrome()

    def scrape_for_rentals(self) -> List[Rental]:
        links = self._scrape_for_links()
        records = []
        for link in links:
            records.append(self._scrape_rental(link))
        rentals = pd.DataFrame.from_records(records)
        rentals = postprocess(rentals)
        return [unmarshal_row(row)
                for row in rentals.to_dict(orient='records')]

    def _scrape_for_links(self) -> List[str]:
        page = 1
        links = []
        while True:
            url = f'{self.base_url}{self.endpoint}'
            if page != 1:
                url += f'-pagina-{page}'
            url += '.html'
            self.driver.get(url)
            links += [
                e.get_attribute('href') for e in
                self.driver.find_elements_by_xpath(
                    '//a[contains(@class, "go-to-posting")]'
                )
            ]
            try:
                self.driver.find_element_by_xpath(
                    '//a[contains(@aria-label, "Siguiente página")]'
                )
            except:
                break

            page += 1
            self.driver.delete_all_cookies()
        return links

    def _scrape_rental(self, link) -> dict:
        self.driver.delete_all_cookies()
        self.driver.get(link)
        title = self._scrape_title()
        description = self._scrape_description()
        extras = self._scrape_extras()
        price = self._scrape_price()
        expenses = self._scrape_expenses()
        location = self._scrape_location()
        rooms = self._scrape_feature('Ambiente')
        covered_surface = self._scrape_feature('Cubierta')
        total_surface = self._scrape_feature('Total')
        return {'title': title,
                'description': description,
                'extras': extras,
                'price': price,
                'expenses': expenses,
                'location': location,
                'link': link,
                'total_surface': total_surface,
                'covered_surface': covered_surface,
                'rooms': rooms}

    def _scrape_title(self) -> str:
        xpath = (
            '//section[contains(@class, "article-section-description")]//h1'
        )
        elem = self.driver.find_element_by_xpath(xpath)
        return elem.get_attribute('innerHTML')

    def _scrape_description(self) -> str:
        xpath = '//div[@id="longDescription"]/div'
        elem = self.driver.find_element_by_xpath(xpath)
        return elem.get_attribute('innerHTML')

    def _scrape_extras(self) -> List[str]:
        xpath = '//div[@id="reactGeneralFeatures"]//ul/li/h4'
        try:
            elems = self.driver.find_elements_by_xpath(xpath)
        except:
            return []
        return [e.get_attribute('innerHTML').strip().lower()
                for e in elems]

    def _scrape_price(self) -> Optional[float]:
        xpath = (
            '//div[contains(@class, "block-price") and '
            'contains('
            './/div[contains(@class, "price-operation")], "Alquiler")]'
            '//div[@class="price-items"]/span/span'
        )
        try:
            elem = self.driver.find_element_by_xpath(xpath)
        except:
            return None
        price = elem.get_attribute('innerHTML')
        if not price:
            return price
        if 'USD' in price:
            return None
        try:
            return float(price.replace('.', '').split(' ')[1])
        except:
            return None

    def _scrape_expenses(self) -> Optional[float]:
        xpath = '//div[contains(@class, "block-expensas")]/span'
        try:
            elem = self.driver.find_element_by_xpath(xpath)
        except:
            return None
        expenses = elem.get_attribute('innerHTML')
        if not expenses:
            return expenses
        if 'USD' in expenses:
            return None
        return float(expenses.replace('.', '').split(' ')[1])

    def _scrape_location(self) -> Optional[str]:
        xpath = '//h2[contains(@class, "title-location")]'
        try:
            elem = self.driver.find_element_by_xpath(xpath)
        except:
            return ''
        location = elem.get_attribute('innerHTML')
        if not location:
            return location

        return normalize_html_string(location)

    def _scrape_feature(self, feature_name) -> Optional[int]:
        xpath = ('//ul[contains(@class, "section-icon-features")]'
                 f'/li[text()[contains(., "{feature_name}")]]')
        try:
            elem = self.driver.find_element_by_xpath(xpath)
        except:
            return None
        feature = elem.text
        feature = re.sub("[^0-9]", "", feature)
        return int(feature)
