"""
backend.model — HuggingFace model initialization package.

Public API (identical to the old flat backend/model.py):

    from backend.model import create_hf_model

Internal sub-modules
--------------------
quantization  — get_quant_config() (optional bitsandbytes 4-bit setup)
hf_model      — create_hf_model(), CustomChatHuggingFace
"""

from backend.model.hf_model import create_hf_model

__all__ = ["create_hf_model"]
