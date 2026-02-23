"""
MedGemma model loader and inference.

Loads the model locally on GPU with optional 4-bit quantisation.
Provides sync and streaming inference via HuggingFace transformers.
"""

from __future__ import annotations

import gc
from threading import Thread
from typing import Callable, Optional

import torch
from transformers import (
    AutoModelForImageTextToText,
    AutoProcessor,
    BitsAndBytesConfig,
    TextIteratorStreamer,
)

from contextmed.config import Settings


class MedGemmaClient:
    """Wraps MedGemma model loading and inference."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load(self) -> None:
        """Load model and processor onto GPU."""
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        model_id = self.settings.model_id

        self.processor = AutoProcessor.from_pretrained(model_id)

        if self.settings.quantize_4bit and torch.cuda.is_available():
            try:
                qconfig = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.bfloat16,
                )
                self.model = AutoModelForImageTextToText.from_pretrained(
                    model_id,
                    quantization_config=qconfig,
                    device_map="auto",
                )
            except Exception:
                self.model = AutoModelForImageTextToText.from_pretrained(
                    model_id,
                    torch_dtype=torch.bfloat16,
                    device_map="auto",
                )
        else:
            self.model = AutoModelForImageTextToText.from_pretrained(
                model_id,
                torch_dtype=torch.bfloat16,
                device_map="auto",
            )

        self.model.eval()

    def generate(
        self,
        prompt: str,
        max_tokens: int | None = None,
        stream: bool = False,
        callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """
        Generate a response from MedGemma.

        Args:
            prompt:     The text prompt to send.
            max_tokens: Max new tokens (defaults to settings value).
            stream:     If True, prints tokens as they are generated.
            callback:   Optional function called with each new token.

        Returns:
            The full generated text.
        """
        if self.model is None or self.processor is None:
            raise RuntimeError("Model not loaded. Call .load() first.")

        max_tokens = max_tokens or self.settings.max_generation_tokens

        messages = [
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        ]

        inputs = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.model.device)

        streamer = TextIteratorStreamer(
            self.processor.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )

        gen_kwargs = dict(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=False,
            streamer=streamer,
        )

        thread = Thread(target=self.model.generate, kwargs=gen_kwargs)
        thread.start()

        full_response = ""
        for token in streamer:
            full_response += token
            if stream:
                print(token, end="", flush=True)
            if callback:
                callback(token)

        thread.join()
        if stream:
            print()

        return full_response.strip()

    @property
    def gpu_memory_gb(self) -> float:
        if torch.cuda.is_available():
            return torch.cuda.memory_allocated() / 1024**3
        return 0.0
