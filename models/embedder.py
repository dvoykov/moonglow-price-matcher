from sentence_transformers import SentenceTransformer
import torch
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

    def __init__(self, model_name: str = 'cointegrated/rubert-tiny2', use_gpu: bool = False):
        """
        Initialize the ProductEmbedder with a SentenceTransformer model.

        Args:
            model_name (str): The name of the SentenceTransformer model to use. Defaults to 'cointegrated/rubert-tiny2'.
            use_gpu (bool): Flag indicating whether to use GPU if available.
        """
        try:
            device = "cuda" if torch.cuda.is_available() and use_gpu else "cpu"
            self.model = SentenceTransformer(model_name, device=device)
        except Exception as e:
            self.model = None
            logger.exception(f'Error loading "{model_name}" model: {e}')
            raise RuntimeError(f"Failed to load the model '{self.model_name}' on the specified device '{device}'")

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
