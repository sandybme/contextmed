"""
Configuration management for ContextMed.

Supports three environments:
  1. Kaggle notebooks  — reads from kaggle_secrets
  2. Local development — reads from .env file
  3. Environment vars  — reads from os.environ
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional


def _is_kaggle() -> bool:
    return os.path.exists("/kaggle/working")


@dataclass(frozen=True)
class Settings:
    """Immutable application settings loaded once at startup."""

    # HuggingFace — required to download MedGemma weights
    hf_token: str = ""

    # Tavily — for clinical guideline web search
    tavily_api_key: str = ""

    # Ngrok — to expose FastAPI from Kaggle
    ngrok_token: str = ""

    # Model
    model_id: str = "google/medgemma-4b-it"
    quantize_4bit: bool = True
    max_generation_tokens: int = 1024
    device: str = "auto"

    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    @property
    def is_kaggle(self) -> bool:
        return _is_kaggle()


def load_settings() -> Settings:
    """Load settings from the best available source."""

    if _is_kaggle():
        return _load_from_kaggle()
    return _load_from_env()


def _load_from_kaggle() -> Settings:
    """Load API keys from Kaggle Secrets."""
    from kaggle_secrets import UserSecretsClient

    secrets = UserSecretsClient()

    def _get(name: str) -> str:
        try:
            return secrets.get_secret(name) or ""
        except Exception:
            return ""

    return Settings(
        hf_token=_get("huggingface"),
        tavily_api_key=_get("TAVILY_API_KEY"),
        ngrok_token=_get("ngrok"),
    )


def _load_from_env() -> Settings:
    """Load from environment variables / .env file."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    return Settings(
        hf_token=os.getenv("HF_TOKEN", ""),
        tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
        ngrok_token=os.getenv("NGROK_TOKEN", ""),
        model_id=os.getenv("MODEL_ID", "google/medgemma-4b-it"),
        quantize_4bit=os.getenv("QUANTIZE_4BIT", "true").lower() == "true",
        max_generation_tokens=int(os.getenv("MAX_GENERATION_TOKENS", "1024")),
    )
