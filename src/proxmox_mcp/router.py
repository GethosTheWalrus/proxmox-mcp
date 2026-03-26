"""Semantic tool router using fastembed for embedding-based similarity search.

At startup, embeds every registered tool's name + description into a vector.
When route_tools is called, embeds the query and returns the top-k most
similar tools by cosine similarity.  Instant on CPU (~5-10ms per query).
"""

from __future__ import annotations

import logging
import os

import numpy as np

logger = logging.getLogger(__name__)

# How many tools to return per routing query
DEFAULT_TOP_K = 20


class ToolRouter:
    """Routes user queries to relevant Proxmox tools via embedding similarity."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        from fastembed import TextEmbedding

        logger.info("Loading embedding model %s ...", model_name)
        cache_dir = os.environ.get("FASTEMBED_CACHE_DIR")
        self._model = TextEmbedding(model_name, cache_dir=cache_dir)
        self._tool_names: list[str] = []
        self._tool_embeddings: np.ndarray | None = None
        logger.info("Embedding model loaded")

    def index(self, tools: list[tuple[str, str]]) -> None:
        """Build the tool embedding index.

        Args:
            tools: List of (name, description) pairs for every registered tool.
        """
        self._tool_names = [name for name, _ in tools]
        texts = [f"{name}: {desc}" for name, desc in tools]
        self._tool_embeddings = np.array(list(self._model.embed(texts)))
        logger.info("Indexed %d tool embeddings", len(self._tool_names))

    def search(self, query: str, top_k: int = DEFAULT_TOP_K) -> list[str]:
        """Return the top-k most relevant tool names for *query*.

        Args:
            query: Natural-language description of what the user wants to do.
            top_k: Number of tool names to return.

        Returns:
            List of tool names, most relevant first.
        """
        if self._tool_embeddings is None or len(self._tool_names) == 0:
            return []

        query_vec = np.array(list(self._model.embed([query])))[0]
        scores = self._tool_embeddings @ query_vec
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [self._tool_names[i] for i in top_indices]


_router: ToolRouter | None = None


def get_router() -> ToolRouter | None:
    """Return the singleton router if TOOL_ROUTING=true."""
    global _router
    if _router is not None:
        return _router

    enabled = os.environ.get("TOOL_ROUTING", "").lower() in ("1", "true", "yes")
    if not enabled:
        return None

    _router = ToolRouter()
    return _router
