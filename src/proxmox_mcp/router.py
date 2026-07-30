"""Semantic tool router using fastembed for embedding-based similarity search.

At startup, embeds every registered tool's name + description into a vector.
When route_tools is called, embeds the query and returns the top-k most
similar tools by cosine similarity.  Instant on CPU (~5-10ms per query).
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# How many tools to return per routing query
DEFAULT_TOP_K = 20


class ToolRouter:
    """Routes user queries to relevant Proxmox tools via embedding similarity."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        import numpy as np
        from fastembed import TextEmbedding

        logger.info("Loading embedding model %s ...", model_name)
        cache_dir = os.environ.get("FASTEMBED_CACHE_DIR")
        self._np = np
        self._model = TextEmbedding(model_name, cache_dir=cache_dir)
        self._tool_names: list[str] = []
        self._tool_embeddings: Any | None = None
        logger.info("Embedding model loaded")

    def index(self, tools: list[tuple[str, str]]) -> None:
        """Build the tool embedding index.

        Args:
            tools: List of (name, description) pairs for every registered tool.
        """
        self._tool_names = [name for name, _ in tools]
        texts = [f"{name}: {desc}" for name, desc in tools]
        embeddings = self._np.array(list(self._model.embed(texts)))
        norms = self._np.linalg.norm(embeddings, axis=1, keepdims=True)
        self._tool_embeddings = embeddings / self._np.clip(norms, 1e-12, None)
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

        query_vec = self._np.array(list(self._model.embed([query])))[0]
        query_norm = self._np.linalg.norm(query_vec)
        if query_norm > 0:
            query_vec = query_vec / query_norm
        scores = self._tool_embeddings @ query_vec
        top_indices = self._np.argsort(scores)[::-1][:top_k]
        return [self._tool_names[i] for i in top_indices]


_router: ToolRouter | None = None
_router_error: str | None = None


def get_router() -> ToolRouter | None:
    """Return the singleton router if TOOL_ROUTING=true."""
    global _router, _router_error
    if _router is not None:
        return _router
    if _router_error is not None:
        return None

    enabled = os.environ.get("TOOL_ROUTING", "").lower() in ("1", "true", "yes")
    if not enabled:
        return None

    try:
        _router = ToolRouter()
    except ImportError as exc:
        _router_error = f"{exc.name or exc} is not installed"
        logger.warning("Tool routing unavailable: %s", _router_error)
        return None
    return _router


def get_router_error() -> str | None:
    """Return the router initialisation error, if one occurred."""
    return _router_error
