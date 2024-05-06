from typing import Tuple
from parsers.base import Product, BaseParser
from tqdm import tqdm
from bs4 import BeautifulSoup
from loguru import logger
import requests
import re
import math


class MoonGlowParser(BaseParser):
    """Parser for the MoonGlow website.

    This class inherits from BaseParser and is used to parse the product catalog from the MoonGlow website.
    """

    def parse_catalog(self) -> Tuple[int, str]:
        """Parses the product catalog from the MoonGlow website.

        Iterates through the catalog pages and extracts product information.

        Returns:
            Tuple[int, str]: A tuple containing the parsing status (0 for success, non-zero for error) and a message.
        """
        self.products.clear()
        max_pages = self._get_max_pages()

        if max_pages == 0:
            logger.warning('The number of pages in the catalog is 0.')
            return 0, 'OK'

        try:
            for url in self.prod_urls:
                loop = 0
                logger.info(f'url: {url}')

                for i in (pbar:=tqdm(range(1, max_pages + 1))):
                    pbar.set_description(f'{len(self.products)} products')

                    response = requests.get(url.format(page=i, loop=loop), headers=self.headers)
                    soup = BeautifulSoup(response.content, "html.parser")

                    if (response.status_code != 200):
                        if response.status_code == 404:
                            logger.wa(f'Exit! Page #{i}: 404 error.')
                            break
                        else:
                            print(f"Page #{i} status_code: {response.status_code}")
                            continue

                    page_products = soup.findAll("div", {"class": r'\"wd-entities-title\"'})

                    if len(page_products) != 0:
                        for item in page_products:
                            item_head = item.select('a[href]')[0]
                            item_url = item_head['href'].replace('\\', '').strip('"''"')

                            self.products.append(Product(source=self.parser_type, url=item_url))

                        loop += len(page_products)
        except Exception as e:
            return 1, e.args[0]

        return 0, 'OK'

    def _parse_single_product(self, product: Product) -> Tuple[int, str]:
        """Parses the details of a single product from its webpage.

        Extracts the product name, description, price, and image URL from the product's webpage.

        Args:
            product (Product): The product object to be updated with details.

        Returns:
            Tuple[int, str]: A tuple containing the parsing status (0 for success, non-zero for error) and a message.
        """
        try:
            response = requests.get(product.url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            product.name = soup.find('h1', class_='product_title entry-title wd-entities-title').get_text(strip=True)

            product.description = soup.find('div', class_='wc-tab-inner wd-scroll-content').get_text(strip=True)

            product.price = soup.findAll('span', class_='woocommerce-Price-amount amount')[-1].\
                get_text(strip=True).lower().strip('mdl').replace(',', '.')

            image_element = soup.find('img', class_='wp-post-image wp-post-image')
            if image_element:
                product.image_url = soup.find('img', class_='wp-post-image wp-post-image')['src']
        except Exception as e:
            return 1, e.args[0]

        return 0, 'OK'

    def _get_max_pages(self, url: str = None) -> int:
        """
        Gets the maximum number of pages in the catalog

        Returns:
            int: The maximum number of pages in the catalog.
        """
        pattern = r'Отображение \d+–\d+ из (\d+)'
        url = 'https://moonglow.md/ru/catalog/'

        max_pages = 0
        products_per_page = 30

        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            element_count = soup.find('p', class_='woocommerce-result-count')

            if element_count:
                products_qty = element_count.get_text()
                match = re.search(pattern, products_qty)

                if match:
                    max_pages = math.ceil(int(match.group(1)) / products_per_page)
        except Exception as e:
            logger.exception(f'Unable to determine the number of pages in the catalog: {e}.')

        return max_pages
