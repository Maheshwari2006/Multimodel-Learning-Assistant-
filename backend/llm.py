"""Ollama wrapper for the Multimodel Learning Assistant."""

import os
import traceback

import ollama


OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))


class LLMUnavailable(Exception):
    """Ollama is unavailable or the model request failed."""


class OllamaLLM:
    def __init__(self):
        self.client = ollama.Client(
            host=OLLAMA_HOST,
            timeout=18000,
        )

    def chat(
        self,
        messages,
        json_mode: bool = False,
        temperature: float = 0.3,
    ) -> str:
        kwargs = {
            "options": {
                "temperature": temperature,
                "num_ctx": OLLAMA_NUM_CTX,
            }
        }

        if json_mode:
            kwargs["format"] = "json"

        try:
            response = self.client.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                **kwargs,
            )

            return response["message"]["content"]

        except Exception as exc:
            print("\n========== OLLAMA ERROR ==========")
            traceback.print_exc()
            print("==================================\n")

            raise LLMUnavailable(
                f"Ollama request failed: {type(exc).__name__}: {exc}"
            ) from exc


llm = OllamaLLM()