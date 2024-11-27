from dataclasses import dataclass
from typing import List, Tuple
from parsers.product import Product
from db.connector import SQLiteConnector
from models.embedder import ProductEmbedder
from config import user_agent, parser_types, db_params
import validators
from tqdm import tqdm


@dataclass
class BaseParser:
    """
    Base class for parsers.

    Attributes:
    - parser_type (str): The type of parser to use.
    - prod_urls (List[str]): The list of urls to parse
    - headers (dict): The headers to be used in HTTP requests.
    - products (List[Product]): A list to store the parsed products.

    Methods:
    - __init__(self, parser_type: str, prod_urls: List[str]): Initializes the BaseParser.
    - __post_init__(self): Performs post-initialization checks and setup.
    - parse_catalog(self) -> Tuple[int, str]: Parses the catalog of products.
    - _parse_single_product(self, product: Product) -> Tuple[int, str]: Parses a single product.
    - save_single_product(conn: SQLiteConnector, p: Product) -> Tuple[int, str]: Saves a single product to the database.
    - parse_products(self) -> Tuple[int, int]: Parses all products in the list.
    - gen_embeddings(self) -> Tuple[int, int]: Generates embeddings for the products in the list.
    - save_products(self) -> Tuple[int, int]: Saves all products in the list to an SQLite database and tracks the progress.
    """

    def __init__(self, parser_type: str, prod_urls: List[str]):
        """
        Initialize the BaseParser.

        Args:
        - parser_type (str): The type of parser to use.
        - prod_urls (str): The list of urls to parse

        Raises:
        - ValueError: If `parser_type` is not valid, one of the urls is not a valid URL or the list of urls is empty
        - RuntimeError: If there is an error while loading the embedder.
        """
        self.parser_type = parser_type
        self.prod_urls = prod_urls
        self.headers = {"User-Agent": user_agent}
        self.products: List[Product] = []

        self.embedder = ProductEmbedder("sentence-transformers/all-MiniLM-L6-v2")

        if self.embedder.model is None:
            raise RuntimeError("Error while loading embedder.")

    def __post_init__(self):
        """
        Perform post-initialization checks and setup.

        Raises:
        - RuntimeError: If there is an error while loading the embedder.
        """
        if self.parser_type not in parser_types:
            raise ValueError(
                f"`parser_type` must be one of the following: {parser_types}"
            )

        if not self.prod_urls:
            raise ValueError("The list of urls to parse is empty.")

        for url in self.prod_urls:
            if not validators.url(url):
                raise ValueError(f"The passed url `{url}` is not valid.")

    def parse_catalog(self) -> Tuple[int, str]:
        """
        Parses the catalog of products.

        Returns:
            Tuple[int, str]: A tuple containing the parsing status (0 for success, non-zero for error) and a message.
        """
        pass

    def _parse_single_product(self, product: Product) -> Tuple[int, str]:
        """
        Parses a single product.

        Args:
            product (Product): The product to parse.

        Returns:
            Tuple[int, str]: A tuple containing the parsing status (0 for success, non-zero for error) and a message.
        """
        pass

    def _get_max_pages(self, url: str = None) -> int:
        """
        Gets the maximum number of pages in the catalog or for a specific product category.

        Args:
            url (str, optional): The URL of the catalog or product category. If not provided, the hard-coded URL will be used.

        Returns:
            int: The maximum number of pages in the catalog or product category.
        """
        pass

    @staticmethod
    def save_single_product(conn: SQLiteConnector, p: Product) -> Tuple[int, str]:
        query = """
            insert or replace into products (source, url, name, description, price, image_url, name_emb, descr_emb)
            values(?, ?, ?, ?, ?, ?, ?, ?)
        """

        name_emb = None if p.name_emb is None else p.name_emb.tobytes()
        descr_emb = None if p.descr_emb is None else p.descr_emb.tobytes()

        params = (
            p.source,
            p.url,
            p.name,
            p.description,
            p.price,
            p.image_url,
            name_emb,
            descr_emb,
        )

        status_code, status_message = conn.execute_query(query, params)

        return status_code, status_message

    def parse_products(self) -> Tuple[int, int]:
        """
        Parses all products in the list.

        Returns:
            Tuple[int, int]: A tuple containing the total number of products processed and the number of errors encountered.
        """
        err_qty = 0
        prc_qty = 0

        for product in (pbar := tqdm(self.products)):
            pbar.set_description(f"Product #{prc_qty + 1} processed ...")

            status_code, status_message = self._parse_single_product(product)

            if status_code != 0:
                print(f"Product parsing error: {product}")
                print(f"Reason: {status_message}")
                print("")
                err_qty += 1

            prc_qty += 1

        return prc_qty, err_qty

    def gen_embeddings(self) -> Tuple[int, int]:
        """
        Generate embeddings for the products in the controller.

        This method iterates over each product in the controller and generates embeddings for
        the product's name and description using the embedder specified in the controller.

        Returns:
            Tuple[int, int]: A tuple containing the total number of products processed and the number
                of errors encountered during embedding generation.
        """
        err_qty = 0
        prc_qty = 0

        for product in (pbar := tqdm(self.products)):
            pbar.set_description(f"Product #{prc_qty + 1} processed ...")

            product.name_emb = self.embedder.embed_description(product.name)
            product.descr_emb = self.embedder.embed_description(product.description)

            if product.name_emb is None:
                print(f"Error generating embedding for product name: {product}")
                err_qty += 1

            if product.descr_emb is None:
                print(f"Error generating embedding for product description: {product}")
                err_qty += 1

            prc_qty += 1

        return prc_qty, err_qty

    def save_products(self) -> Tuple[int, int]:
        """
        Saves all products in the list to an SQLite database and tracks the progress.

        This function attempts to connect to an SQLite database and iterates through
        each product in the product list. Each product is saved using the
        save_single_product method. It provides feedback on the progress and logs any errors encountered.

        Returns:
            Tuple[int, int]: A tuple containing the total number of products saved and the number of errors encountered.
        """
        conn = SQLiteConnector(db_params["db_file"])
        status_code, status_message = conn.connect()

        if status_code != 0:
            print(status_message)
            return 0, 0

        err_qty = 0
        svd_qty = 0

        for product in (pbar := tqdm(self.products)):
            pbar.set_description(f"Product #{svd_qty + 1} saved ...")

            status_code, status_message = BaseParser.save_single_product(conn, product)

            if status_code != 0:
                print(f"Product saving error: {product}")
                print(f"Reason: {status_message}")
                print("")
                err_qty += 1

            svd_qty += 1

        conn.close()

        return svd_qty, err_qty
