"""
OpenBayan Next — Qdrant Vector Service
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Provides asynchronous vector retrieval with Binary Quantization (BQ)
and on-disk Float32 oversampled rescoring.
"""

import os
import logging
from typing import List, Tuple
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

logger = logging.getLogger("openbayan.qdrant")

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "shamela_11m")


class QdrantService:
    def __init__(self):
        self.client: AsyncQdrantClient | None = None
        self.collection_name = QDRANT_COLLECTION
        self.url = QDRANT_URL

    async def connect(self):
        try:
            self.client = AsyncQdrantClient(url=self.url, timeout=10.0, check_compatibility=False)
            collections = await self.client.get_collections()
            existing = [c.name for c in collections.collections]
            if self.collection_name in existing:
                logger.info(f"Connected to Qdrant at {self.url}, collection '{self.collection_name}' ready.")
            else:
                logger.warning(f"Connected to Qdrant at {self.url}, but collection '{self.collection_name}' not found.")
        except Exception as e:
            logger.warning(f"Qdrant connection warning ({self.url}): {e}")
            self.client = None

    async def close(self):
        if self.client:
            await self.client.close()
            self.client = None

    async def search(
        self,
        query_vector: List[float],
        limit: int = 50,
        oversampling: float = 3.0
    ) -> List[Tuple[str, float]]:
        """
        Executes 1-bit Binary Quantization Hamming distance search in RAM,
        then rescores top (limit * oversampling) candidates against on-disk FP32 vectors.
        """
        if not self.client:
            return []

        try:
            results = await self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                search_params=models.SearchParams(
                    quantization=models.QuantizationSearchParams(
                        rescore=True,
                        oversampling=oversampling
                    )
                ),
                with_payload=False,  # Zero-payload: fetch raw text from SQLite on demand
                with_vectors=False
            )
            return [(str(hit.id), float(hit.score)) for hit in results.points]
        except Exception as e:
            logger.error(f"Qdrant query_points error: {e}")
            return []


qdrant = QdrantService()
