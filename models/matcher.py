import numpy as np
from parsers.product import Product
from typing import List, Tuple, Optional
from tqdm import tqdm


class Matcher:
    """Class to match products from two lists based on maximum cosine similarity."""

    def __init__(self, products_a: List[Product], products_b: List[Product], threshold: float = 0.9):
        self.products_a = products_a
        self.products_b = products_b
        self.matches: List[Tuple[Product, Optional[Product], float]] = []
        self.threshold = threshold

    @staticmethod
    def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate the cosine similarity between two vectors."""
        if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
            return 0.0

        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    def find_best_matches(self):
        """Find the best match for each product in list A from list B based on maximum cosine similarity."""
        for prod_a in tqdm(self.products_a, desc='Matching Products', unit='product'):
            best_match = None
            max_similarity = -1

            for prod_b in self.products_b:
                if prod_a.descr_emb is not None and prod_b.descr_emb is not None:
                    sim = self.cosine_similarity(prod_a.name_emb, prod_b.name_emb)

                    if sim > max_similarity:
                        max_similarity = sim
                        best_match = prod_b

            if max_similarity >= self.threshold:
                self.matches.append((prod_a, best_match, max_similarity))

    def get_matches(self) -> List[Tuple[Product, Optional[Product], float]]:
        """Return the list of product pairs with their cosine similarity."""
        return self.matches
