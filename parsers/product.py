from dataclasses import dataclass
import numpy as np


@dataclass
class Product:
    """A class to represent a product.

    Attributes:
        id (int): The ID of the product.
        source (str): The source of the product.
        url (str): The URL of the product.
        name (str): The name of the product.
        description (str): The description of the product.
        price (float): The price of the product.
        image_url (str): The URL of the product's image.
        name_emb (np.ndarray): An array representing the name embedding of the product.
        descr_emb (np.ndarray): An array representing the description embedding of the product.

    Methods:
        __str__: Returns a string representation of the product.
    """

    def __init__(
        self, source: str, url: str, name: str = "", price: float = None
    ) -> None:
        self.id: int = 0
        self.source = source
        self.url = url
        self.name = name
        self.description: str = ""
        self.price = price
        self.image_url: str = ""
        self.name_emb: np.ndarray = None
        self.descr_emb: np.ndarray = None

    def __str__(self):
        return (
            f"id: {self.id}\n"
            f"source: {self.source}\n"
            f"url: {self.url}\n"
            f"name: {self.name}\n"
            # f"description: {self.description}\n"
            f"price: {self.price}\n"
            f"image url: {self.image_url}"
        )
