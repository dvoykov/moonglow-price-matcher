from typing import Tuple, List, Dict
from parsers.base import Product
from config import db_params
from db.connector import SQLiteConnector
import numpy as np


class ProductController:
    """A class to handle products and their embeddings from a database.

    Methods:
        get_products: Retrieves products from the database for a given source.
        get_embeddings: Retrieves embeddings for products from the database for a given source.
    """
    @staticmethod
    def get_products(source: str) -> Tuple[int, str, List[Product]]:
        """Retrieve products from the database for a given source.

        Args:
            source (str): The source of the products.

        Returns:
            Tuple[int, str, List[Product]]: A tuple containing status code, status message,
                and a list of Product objects.
        """
        conn = SQLiteConnector(db_params['db_file'])
        status_code, status_message = conn.connect()

        if status_code != 0:
            return status_code, status_message, []

        query = 'select * from products where source = ?;'
        params = (source,)

        status_code, status_message, result = conn.execute_read_query(query, params)

        if status_code != 0:
            return status_code, status_message, []

        products = []

        for id, _, url, name, descr, price, image_url, name_emb, descr_emb in result:
            product = Product(
                source=source,
                url=url,
            )

            product.id=id
            product.name=name
            product.description=descr
            product.price=price
            product.image_url=image_url
            product.name_emb=np.frombuffer(name_emb, dtype=np.float32)
            product.descr_emb=np.frombuffer(descr_emb, dtype=np.float32)

            products.append(product)

        conn.close()

        return 0, 'OK', products

    @staticmethod
    def get_embeddings(source: str) -> Tuple[int, str, List[Dict]]:
        """Retrieve embeddings for products from the database for a given source.

        Args:
            source (str): The source of the products.

        Returns:
            Tuple[int, str, List[Dict]]: A tuple containing status code, status message,
                and a list of dictionaries containing product embeddings.
        """
        conn = SQLiteConnector(db_params['db_file'])
        status_code, status_message = conn.connect()

        if status_code != 0:
            return status_code, status_message, []

        query = 'select id, name_emb, descr_emb from products where source = ?;'
        params = (source,)

        status_code, status_message, result = conn.execute_read_query(query, params)

        if status_code != 0:
            return status_code, status_message, []

        embeddings = []

        for id, name_emb, descr_emb in result:
            embedding = {
                'source': source,
                'product_id': id,
                'name_emb': np.frombuffer(name_emb, dtype=np.float32),
                'descr_emb': np.frombuffer(descr_emb, dtype=np.float32)
            }

            embeddings.append(embedding)

        conn.close()

        return 0, 'OK', embeddings
