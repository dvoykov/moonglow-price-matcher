from sentence_transformers import SentenceTransformer
import numpy as np
from loguru import logger

class ProductEmbedder:
    """
    A class for embedding product descriptions using SentenceTransformer.

    Example:
        embedder = ProductEmbedder()
        description = "This is a product description."
        embedding = embedder.embed_description(description)
    """

    def __init__(self, model_name: str = 'cointegrated/rubert-tiny2'):
        """
        Initialize the ProductEmbedder with a SentenceTransformer model.

        Args:
            model_name (str): The name of the SentenceTransformer model to use. Defaults to 'cointegrated/rubert-tiny2'.
        """
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            self.model = None
            logger.exception(f'Error loading "{model_name}" model: {e}')

    def embed_description(self, description) -> np.ndarray:
        """
        Embed a product description using the initialized SentenceTransformer model.

        Args:
            description (str): The product description to embed.

        Returns:
            np.ndarray or None: The embedded representation of the description,
                                 or None if the model is not loaded.
        """
        if self.model:
            embedding = self.model.encode(description)
            return embedding

        return None
