from typing import Tuple, List
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
            brand_urls = self._get_brands()

            for brand_url in brand_urls:
                logger.info(f"brand_url: {brand_url}")

                max_pages = self._get_max_pages(brand_url)
                if max_pages == 0:
                    logger.warning("The number of pages for category is 0.")
                    continue

                for i in (pbar := tqdm(range(1, max_pages + 1))):
                    pbar.set_description(f"{len(self.products)} products")

                    response = requests.get(
                        url=f"{brand_url}?page={i}", headers=self.headers
                    )
                    soup = BeautifulSoup(response.content, "html.parser")

                    if response.status_code != 200:
                        if response.status_code == 404:
                            logger.warning(f"Exit! Page #{i}: 404 error.")
                            break
                        else:
                            print(f"Page #{i} status_code: {response.status_code}")
                            continue

                    for product in soup.find_all("div", class_="product-block"):
                        title = product.find("a", class_="title").text.strip()
                        href = product.find("a", class_="title")["href"]

                        curr_price = (
                            float(
                                product.find("span", class_="new-price").text.strip(
                                    " MDL"
                                )
                            )
                            if product.find("span", class_="new-price")
                            else None
                        )

                        if not curr_price:
                            curr_price = (
                                float(
                                    product.find("span", class_="price").text.strip(
                                        " MDL"
                                    )
                                )
                                if product.find("span", class_="price")
                                else None
                            )
                        # old_price = (
                        #     float(product.find("span", class_="old-price").text.strip(" MDL"))
                        #     if product.find("span", class_="old-price")
                        #     else None
                        # )

                        self.products.append(
                            Product(
                                source=self.parser_type,
                                url=f"https://myskin.md{href}",
                                name=title,
                                price=curr_price,
                            )
                        )

        except Exception as e:
            logger.exception(f"Exception while parsing page with products: {e}")
            return 1, e.args[0]

        return 0, "OK"

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
            soup = BeautifulSoup(response.text, "html.parser")

            description_title = soup.find("span", class_="acc-title", string="Описание")
            if description_title:
                description_item = description_title.find_parent(
                    "li", class_="acc-block_item"
                )

                if description_item:
                    description_content = description_item.find(
                        "div", class_="acc-content"
                    )

                    if description_content:
                        paragraphs = description_content.find_all("p")

                        if paragraphs and paragraphs[0].get_text(strip=True).startswith(
                            "Рекомендуем"
                        ):
                            paragraphs.pop(0)

                        product.description = "\n".join(
                            p.get_text(strip=True) for p in paragraphs
                        )

            a_tag = soup.find("a", class_="gall-img img-0 active")

            if a_tag:
                product.image_url = f"https://myskin.md{a_tag.get('href')}"

        except Exception as e:
            return 1, e.args[0]

        return 0, "OK"

    def _get_max_pages(self, url: str = None) -> int:
        """
        Gets the maximum number of pages for the product category

        Returns:
            int: The maximum number of pages in the catalog.
        """
        max_pages = 1

        try:
            response = requests.get(url=url, headers=self.headers)
            soup = BeautifulSoup(response.content, "html.parser")

            paginator = soup.find("div", class_="paginator_wrapper")

            if paginator:
                max_pages = int(paginator.get("data-pages"))
        except Exception as e:
            max_pages = 0
            logger.exception(
                f"Unable to determine the number of pages for category: {e}."
            )

        return max_pages

    def _get_brands(self) -> List[str]:
        response = requests.get(url=self.prod_urls[0], headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")

        brand_urls = []
        for brand_tag in soup.find_all("a", class_="brand-name"):
            brand_href = brand_tag.get("href")
            brand_urls.append(f"https://myskin.md{brand_href}")

        return brand_urls
