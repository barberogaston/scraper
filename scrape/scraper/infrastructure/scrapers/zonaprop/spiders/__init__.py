import scrapy

from scraper.infrastructure.scrapers.config import SCRAPER_PATH
from scraper.infrastructure.scrapers.utils import normalize_html_string

ZONAPROP_URL = 'https://www.zonaprop.com.ar'
BASE_URL = f'{ZONAPROP_URL}/departamentos-alquiler-nueva-cordoba.html'


class ZonapropSpider(scrapy.Spider):
    name = 'zonaprop'
    start_urls = [BASE_URL]
    page_number = 1

    custom_settings = {
        'FEEDS': {
            f'{SCRAPER_PATH}/{name}_data.json': {
                'format': 'json',
                'encoding': 'utf8',
                'overwrite': True
            }
        },
        'DOWNLOADER_MIDDLEWARES': {
            'scraper.'
            'infrastructure.'
            'scrapers.'
            'zonaprop.'
            'middlewares.'
            'ZonapropDownloaderMiddleware': 543
        }
    }

    def parse(self, response):
        xpath = '//a[contains(@class, "go-to-posting")]/@href'
        posting_endpoints = response.xpath(xpath).getall()
        posting_urls = [f'{ZONAPROP_URL}{endpoint}'
                        for endpoint
                        in posting_endpoints]
        yield from response.follow_all(posting_urls, self.parse_posting)

        xpath = '//a[contains(@aria-label, "Siguiente página")]'
        next_page = response.xpath(xpath)

        if next_page:
            self.page_number += 1
            page = f'-pagina-{self.page_number}.html'
            url = BASE_URL.replace('.html', page)
            yield scrapy.Request(url, callback=self.parse)

    def parse_posting(self, response):
        title = self._get_title_from_posting(response)
        description = self._get_description_from_posting(response)
        extras = self._get_extras_from_posting(response)
        price = self._get_price_from_posting(response)
        expenses = self._get_expenses_from_posting(response)
        rooms = self._get_feature_from_posting(response, 'Ambiente')
        covered_surface = self._get_feature_from_posting(response, 'Cubierta')
        total_surface = self._get_feature_from_posting(response, 'Total')
        location = self._get_location_from_posting(response)
        link = response.url
        json = {'title': title,
                'description': description,
                'extras': extras,
                'price': price,
                'expenses': expenses,
                'location': location,
                'link': link,
                'total_surface': total_surface,
                'covered_surface': covered_surface,
                'rooms': rooms}
        yield json

    def _get_title_from_posting(self, posting):
        xpath = ('//section[contains(@class, "article-section-description")]'
                 '//h1/text()')
        return posting.xpath(xpath).get()

    def _get_description_from_posting(self, posting):
        xpath = '//div[@id="longDescription"]/div/text()'
        return ''.join(posting.xpath(xpath).getall())

    def _get_extras_from_posting(self, posting):
        xpath = '//div[@id="reactGeneralFeatures"]//ul/li/h4/text()'
        return [e.strip().lower() for e in posting.xpath(xpath).getall()]

    def _get_price_from_posting(self, posting):
        xpath = (
            '//div[contains(@class, "block-price") and '
            'contains('
            './/div[contains(@class, "price-operation")], "Alquiler")]'
            '//div[@class="price-items"]/span/span/text()'
        )
        price = posting.xpath(xpath).get()
        if not price:
            return price
        if 'USD' in price:
            return None
        try:
            return float(price.replace('.', '').split(' ')[1])
        except Exception as e:
            self.log(str(e))
            return None

    def _get_expenses_from_posting(self, posting):
        xpath = '//div[contains(@class, "block-expensas")]/span/text()'
        expenses = posting.xpath(xpath).get()
        if not expenses:
            return expenses
        if 'USD' in expenses:
            return None
        return float(expenses.replace('.', '').split(' ')[1])

    def _get_location_from_posting(self, posting):
        xpath = '//h2[contains(@class, "title-location")]/node()'
        location = ''.join(posting.xpath(xpath).getall())
        if not location:
            return location

        return normalize_html_string(location)

    def _get_feature_from_posting(self, posting, feature_name):
        xpath = '//ul[contains(@class, "section-icon-features")]'\
                f'/li[text()[contains(., "{feature_name}")]]/text()[last()]'
        feature = posting.xpath(xpath).get()
        if not feature:
            return feature
        feature = normalize_html_string(feature)
        feature = feature.replace('m²', '').replace(feature_name, '')
        return int(feature)
