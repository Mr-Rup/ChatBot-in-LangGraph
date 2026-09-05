"""
ChatBot class — pairs a language model with its compiled LangGraph.
"""

# Standard library
import logging
from typing import Any, Literal

# Local
from backend.model import create_hf_model
from backend.graph import create_chatbot

logger = logging.getLogger(__name__)


class ChatBot:
    """
    Wrapper that pairs a language model with its compiled LangGraph.

    Attributes
    ----------
    model : Any
        The initialized HuggingFace model wrapper, or None on failure.
    bot : Any
        The compiled LangGraph chatbot graph, or None on failure.
    """

    def __init__(
        self,
        model_type: Literal["api", "local"],
        model_name: str,
        model_task: str,
        model_temperature: float,
        model_max_new_tokens: int,
    ) -> None:
        """
        Build the model and compile the graph.

        The graph is only compiled if the model loaded successfully —
        passing a None model to create_chatbot() would fail cryptically.

        Parameters
        ----------
        model_type : Literal['api', 'local']
            Whether to use a local or API-based HuggingFace model.
        model_name : str
            The HuggingFace repository ID.
        model_task : str
            The pipeline task (e.g., 'text-generation').
        model_temperature : float
            Sampling temperature for generation.
        model_max_new_tokens : int
            Maximum tokens to generate per response.
        """
        self.model = create_hf_model(
            model_type, model_name, model_task, model_temperature, model_max_new_tokens
        )

        if self.model is not None:
            self.bot = create_chatbot(self.model)
        else:
            self.bot = None
            logger.error("ChatBot: model initialization returned None — graph not compiled.")
