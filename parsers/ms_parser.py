from typing import Tuple
from parsers.base import Product, BaseParser
from tqdm import tqdm
from bs4 import BeautifulSoup
from loguru import logger
import requests


class MySkinParser(BaseParser):
    """Parser for the MySkin website.

    This class inherits from BaseParser and is used to parse the products from the MySkin website.
    """

    def parse_catalog(self) -> Tuple[int, str]:
        """Parses the product catalog from the MoonGlow MySkin.

        Iterates through the catalog pages and extracts product information.

        Returns:
            Tuple[int, str]: A tuple containing the parsing status (0 for success, non-zero for error) and a message.
        """
        self.products.clear()

        try:
            for url in self.prod_urls:
                logger.info(f'url: {url}')

                max_pages = self._get_max_pages(url)
                if max_pages == 0:
                    logger.warning('The number of pages for category is 0.')
                    continue

                for i in (pbar:=tqdm(range(1, max_pages + 1))):
                    pbar.set_description(f'{len(self.products)} products')

                    response = requests.get(url=f'{url}?page={i}', headers=self.headers)
                    soup = BeautifulSoup(response.content, "html.parser")

                    if (response.status_code != 200):
                        if response.status_code == 404:
                            logger.wa(f'Exit! Page #{i}: 404 error.')
                            break
                        else:
                            print(f"Page #{i} status_code: {response.status_code}")
                            continue

                    page_products = soup.findAll("a", {"class": 'sing-product'})

                    if len(page_products) != 0:
                        for item in page_products:
                            item_url = f'https://myskin.md{item["href"]}'
                            self.products.append(Product(source=self.parser_type, url=item_url))

        except Exception as e:
            logger.exception(f'Exception while parsing page with products: {e}')
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

            product.name = soup.find('h1', class_='product-name').get_text(strip=True)

            product_description_div = soup.find('div', class_='inset-text pd-text')
            if product_description_div:
                product.description = ' '.join([
                    p.get_text(strip=True) for p in product_description_div.find_all(['p', 'li'])
                ])

            product.price = float(soup.find('div', class_='price').get_text(strip=True).lower().split('mdl')[0])

            product.image_url = f'https://myskin.md{soup.find("img", class_="picture")["src"]}'
        except Exception as e:
            return 1, e.args[0]

        return 0, 'OK'

    def _get_max_pages(self, url: str = None) -> int:
        """
        Gets the maximum number of pages for the product category

        Returns:
            int: The maximum number of pages in the catalog.
        """
        max_pages = 1

        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            paginator_div = soup.find('div', class_='paginatorextendwrapper')

            if paginator_div:
                page_products = soup.findAll("a", {"class": 'pagelink'})
                max_pages = len(page_products)
        except Exception as e:
            max_pages = 0
            logger.exception(f'Unable to determine the number of pages for category: {e}.')

        return max_pages
