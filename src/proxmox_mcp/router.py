"""Tool router using a fine-tuned FunctionGemma model to predict relevant tools.

When TOOL_ROUTER_MODEL is set, the router loads the model at startup and
provides fast inference to filter the 285+ tools down to the most relevant
subset for a given user query.
"""

from __future__ import annotations

import json
import logging
import os
import random
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Maximum tools to include in the FunctionGemma prompt (must match training)
MAX_TOOLS_PER_PROMPT = 5
# How many top tools to return to the caller
DEFAULT_TOP_K = 5


def _build_tool_def(name: str, description: str, parameters: dict) -> dict:
    """Build a FunctionGemma-compatible tool definition from MCP tool info."""
    first_line = (description or "").split("\n")[0].strip()
    props = {}
    required = []
    if parameters:
        for pname, pinfo in parameters.get("properties", {}).items():
            props[pname] = {"type": pinfo.get("type", "string")}
            if "description" in pinfo:
                props[pname]["description"] = pinfo["description"]
        required = parameters.get("required", [])
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": first_line,
            "parameters": {
                "type": "object",
                "properties": props,
                **({"required": required} if required else {}),
            },
        },
    }


class ToolRouter:
    """Routes user queries to relevant Proxmox tools using FunctionGemma."""

    def __init__(self, model_dir: str) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoProcessor

        self._model_dir = model_dir
        logger.info("Loading tool router model from %s ...", model_dir)

        self._processor = AutoProcessor.from_pretrained(model_dir)

        use_gpu = torch.cuda.is_available()
        dtype = (
            torch.bfloat16
            if use_gpu and torch.cuda.is_bf16_supported()
            else torch.float32
        )
        self._model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            dtype=dtype,
            device_map="auto" if use_gpu else None,
        )
        self._model.eval()
        self._torch = torch
        logger.info("Tool router model loaded (dtype=%s)", dtype)

    def predict(
        self,
        query: str,
        tool_defs: list[dict],
        top_k: int = DEFAULT_TOP_K,
    ) -> list[str]:
        """Predict the most relevant tool names for *query*.

        Because FunctionGemma was trained with MAX_TOOLS_PER_PROMPT tools per
        example, we run multiple passes with different tool subsets and collect
        votes.  The most-voted tool names are returned.

        Args:
            query: The user's natural-language request.
            tool_defs: Full list of FunctionGemma-format tool definitions.
            top_k: Number of top tools to return.

        Returns:
            Sorted list of up to *top_k* tool names, most relevant first.
        """
        if len(tool_defs) <= top_k:
            return [t["function"]["name"] for t in tool_defs]

        votes: dict[str, int] = {}
        # Number of inference passes to get good coverage
        n_passes = min(max(len(tool_defs) // MAX_TOOLS_PER_PROMPT, 3), 10)

        # Shuffle for randomised subsets
        shuffled = list(tool_defs)

        messages = [
            {"role": "developer", "content": "You are a model that can do function calling with the following functions"},
            {"role": "user", "content": query},
        ]

        for _ in range(n_passes):
            random.shuffle(shuffled)
            subset = shuffled[:MAX_TOOLS_PER_PROMPT]

            inputs = self._processor.apply_chat_template(
                messages,
                tools=subset,
                add_generation_prompt=True,
                return_dict=True,
                return_tensors="pt",
            )
            with self._torch.no_grad():
                out = self._model.generate(
                    **inputs.to(self._model.device),
                    pad_token_id=self._processor.eos_token_id,
                    max_new_tokens=64,
                )
            output = self._processor.decode(
                out[0][len(inputs["input_ids"][0]):],
                skip_special_tokens=True,
            )

            match = re.search(r"call:(\w+)\{", output)
            if match:
                name = match.group(1)
                votes[name] = votes.get(name, 0) + 1

        ranked = sorted(votes, key=lambda n: votes[n], reverse=True)
        return ranked[:top_k]


_router: ToolRouter | None = None


def get_router() -> ToolRouter | None:
    """Return the cached router, loading it on first call if configured."""
    global _router
    if _router is not None:
        return _router

    model_dir = os.environ.get("TOOL_ROUTER_MODEL", "")
    if not model_dir:
        return None

    path = Path(model_dir)
    if not path.exists():
        logger.warning("TOOL_ROUTER_MODEL=%s does not exist, routing disabled", model_dir)
        return None

    _router = ToolRouter(str(path))
    return _router
