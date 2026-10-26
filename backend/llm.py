"""Thin Ollama wrapper. Model names and context size come from environment variables."""
import os

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))   # Ollama's default of 2048 silently truncates RAG prompts


class LLMUnavailable(Exception):
    """Ollama is not reachable or the model is missing."""


class OllamaLLM:
    def chat(self, messages, json_mode: bool = False, temperature: float = 0.3) -> str:
        try:
            import ollama
        except ImportError as exc:
            raise LLMUnavailable("The 'ollama' Python package is not installed (pip install ollama).") from exc
        kwargs = {"options": {"temperature": temperature, "num_ctx": OLLAMA_NUM_CTX}}
        if json_mode:
            kwargs["format"] = "json"
        try:
            response = ollama.chat(model=OLLAMA_MODEL, messages=messages, **kwargs)
        except Exception as exc:
            raise LLMUnavailable(
                f"Could not get a response from Ollama. Make sure Ollama is running and "
                f"'{OLLAMA_MODEL}' is installed (ollama pull {OLLAMA_MODEL})."
            ) from exc
        return response["message"]["content"]


llm = OllamaLLM()
