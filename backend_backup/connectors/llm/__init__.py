"""
LLM Connectors Module
Unified interface for different LLM providers
NO HARDCODED MODELS - All models configured via settings
"""

from .openrouter import OpenRouterLLM

__all__ = ["OpenRouterLLM"]
