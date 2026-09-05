"""
Optional 4-bit quantization configuration for local HuggingFace models.

4-bit quantization reduces VRAM usage by ~75% with minimal quality loss,
making 3B models fit in ~2 GB of VRAM instead of ~8 GB. Requires:
- CUDA-capable NVIDIA GPU
- bitsandbytes package installed

If bitsandbytes is not available (e.g., CPU-only systems or macOS), this
module returns None and the model loads at standard precision instead.
"""

# Standard library
import logging

logger = logging.getLogger(__name__)


def get_quant_config():
    """
    Build a BitsAndBytesConfig for 4-bit quantization, if available.

    Returns
    -------
    BitsAndBytesConfig or None
        A configured quantization object, or None if bitsandbytes or
        torch is not installed.
    """
    try:
        from transformers import BitsAndBytesConfig
        import torch

        config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
        )
        logger.info("4-bit quantization enabled (bitsandbytes detected).")
        return config

    except ImportError:
        logger.info("bitsandbytes not available — loading model at standard precision.")
        return None
