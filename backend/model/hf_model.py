"""
HuggingFace model initialization.

Supports two backends:
- 'api'   : HuggingFaceEndpoint  — calls the HF Inference API (requires HF token)
- 'local' : HuggingFacePipeline  — downloads and runs the model on-device

The CustomChatHuggingFace subclass overrides _to_chat_prompt() to fix a
bug in the default implementation where ToolMessage and tool_calls are
silently stripped from the chat template, breaking multi-turn tool use.
"""

# Standard library
import logging
import traceback
from typing import Any, Literal

# Third-party (loaded after .env and env-vars are applied by caller)
from dotenv import load_dotenv

# Local
from backend.config import load_config, apply_environment_settings
from backend.model.quantization import get_quant_config

logger = logging.getLogger(__name__)

# Apply secrets and environment settings before any HF imports
load_dotenv()
apply_environment_settings()


def create_hf_model(
    type: Literal["api", "local"],
    model_name: str,
    model_task: str,
    model_temperature: float,
    model_max_new_tokens: int,
) -> Any:
    """
    Initialize and return a HuggingFace language model.

    Parameters
    ----------
    type : Literal['api', 'local']
        Backend to use.
    model_name : str
        HuggingFace repo ID (e.g., 'Qwen/Qwen2.5-3B-Instruct').
    model_task : str
        Pipeline task (e.g., 'text-generation').
    model_temperature : float
        Sampling temperature (0 < temperature ≤ 1.0).
    model_max_new_tokens : int
        Max tokens to generate per response.

    Returns
    -------
    CustomChatHuggingFace or None
        The configured model wrapper, or None on failure.
    """
    try:
        from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint, HuggingFacePipeline

        # ── API model ──
        if type == "api":
            logger.info("Initializing HF API model: %s", model_name)
            llm = HuggingFaceEndpoint(
                repo_id=model_name,
                task=model_task,
                pipeline_kwargs=dict(
                    temperature=model_temperature,
                    max_new_tokens=model_max_new_tokens,
                ),
            )

        # ── Local model ──
        elif type == "local":
            logger.info("Initializing local HF model: %s", model_name)

            model_kwargs: dict[str, Any] = {"device_map": "auto", "dtype": "auto"}

            # Attempt 4-bit quantization — reduces VRAM by ~75%
            quant_config = get_quant_config()
            if quant_config is not None:
                model_kwargs["quantization_config"] = quant_config

            from transformers import GenerationConfig

            # Load the model's own generation defaults, then override only our params.
            # This preserves values like eos_token_id and repetition_penalty.
            generation_config = GenerationConfig.from_pretrained(model_name)
            generation_config.max_new_tokens = model_max_new_tokens
            generation_config.do_sample = True
            generation_config.temperature = model_temperature

            llm = HuggingFacePipeline.from_model_id(
                model_id=model_name,
                task=model_task,
                model_kwargs=model_kwargs,
                pipeline_kwargs={
                    "generation_config": generation_config,
                    "return_full_text": False,  # Don't include the prompt in the output
                },
            )

        else:
            raise ValueError(f"model type must be 'api' or 'local', got: {type!r}")

        # ── Custom wrapper to fix ToolMessage handling ──
        class CustomChatHuggingFace(ChatHuggingFace):
            """
            Fixes _to_chat_prompt() to preserve ToolMessage and tool_calls.

            The default implementation calls _to_chatml_format() which silently
            strips ToolMessage objects and drops tool_call metadata from
            AIMessages. This means the LLM never sees tool results on follow-up
            turns, breaking multi-turn tool use.

            This override uses _convert_message_to_dict() instead, which keeps
            the full message structure that the Jinja2 chat template expects.
            """

            def _to_chat_prompt(self, messages) -> str:
                from langchain_huggingface.chat_models.huggingface import _convert_message_to_dict

                if not messages:
                    raise ValueError("At least one message must be provided!")

                messages_dicts = [_convert_message_to_dict(m) for m in messages]
                return self.tokenizer.apply_chat_template(
                    messages_dicts,
                    tokenize=False,
                    add_generation_prompt=True,
                )

        model = CustomChatHuggingFace(llm=llm)
        logger.info("Model '%s' initialized successfully.", model_name)
        return model

    except Exception:
        logger.error("create_hf_model failed for '%s':\n%s", model_name, traceback.format_exc())
        return None
