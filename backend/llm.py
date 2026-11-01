
import os
import traceback
import ollama


LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "cloud" if os.getenv("VERCEL") else "local"
).strip().lower()

LOCAL_OLLAMA_HOST = "http://127.0.0.1:11434"
CLOUD_OLLAMA_HOST = "https://ollama.com"

LOCAL_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")
CLOUD_MODEL = os.getenv("OLLAMA_CLOUD_MODEL", "gemma4:31b")

OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))
OLLAMA_TIMEOUT = 120


class LLMUnavailable(Exception):
    pass


class OllamaLLM:

    def __init__(self):

        if LLM_PROVIDER not in ("local", "cloud"):
            raise ValueError("LLM_PROVIDER must be local or cloud")

        self.provider = LLM_PROVIDER

        self.model = (
            CLOUD_MODEL if self.provider == "cloud"
            else LOCAL_MODEL
        )

        api_key = os.getenv("OLLAMA_API_KEY", "").strip()

        print("========== LLM CONFIGURATION ==========")
        print("LLM PROVIDER:", self.provider)
        print("LLM MODEL:", self.model)
        print("API KEY CONFIGURED:", bool(api_key))
        print("======================================")

        if self.provider == "cloud" and not api_key:
            raise LLMUnavailable("OLLAMA_API_KEY is not configured.")

        headers = {}

        if self.provider == "cloud":
            headers["Authorization"] = f"Bearer {api_key}"

        host = (
            CLOUD_OLLAMA_HOST
            if self.provider == "cloud"
            else LOCAL_OLLAMA_HOST
        )

        self.client = ollama.Client(
            host=host,
            headers=headers,
            timeout=OLLAMA_TIMEOUT
        )

    def chat(
        self,
        messages,
        json_mode=False,
        temperature=0.3
    ):

        kwargs = {
            "options": {
                "temperature": temperature,
                "num_ctx": OLLAMA_NUM_CTX
            }
        }

        if json_mode:
            kwargs["format"] = "json"

        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                **kwargs
            )

            return response["message"]["content"]

        except Exception as exc:
            traceback.print_exc()

            raise LLMUnavailable(
                f"Ollama request failed: {type(exc).__name__}: {exc}"
            ) from exc


llm = OllamaLLM()
