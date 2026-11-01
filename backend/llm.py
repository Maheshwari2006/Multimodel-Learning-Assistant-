
import os
import traceback
import ollama

from google import genai
from google.genai import types


# Use Gemini on Vercel and local Ollama on your computer.
LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "gemini" if os.getenv("VERCEL") else "local"
).strip().lower()

LOCAL_OLLAMA_HOST = "http://127.0.0.1:11434"
LOCAL_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))
OLLAMA_TIMEOUT = 120


class LLMUnavailable(Exception):
    pass


class LLM:

    def __init__(self):
        if LLM_PROVIDER not in ("local", "gemini"):
            raise ValueError(
                "LLM_PROVIDER must be either 'local' or 'gemini'"
            )

        self.provider = LLM_PROVIDER
        self.client = None
        self.model = None

        print("========== LLM CONFIGURATION ==========")
        print("LLM PROVIDER:", self.provider)

        if self.provider == "local":
            self.model = LOCAL_MODEL

            self.client = ollama.Client(
                host=LOCAL_OLLAMA_HOST,
                timeout=OLLAMA_TIMEOUT
            )

        elif self.provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY", "").strip()

            if not api_key:
                raise LLMUnavailable(
                    "GEMINI_API_KEY is not configured."
                )

            self.model = GEMINI_MODEL
            self.client = genai.Client(api_key=api_key)

        print("LLM MODEL:", self.model)
        print("=======================================")

    def chat(
        self,
        messages,
        json_mode=False,
        temperature=0.3
    ):

        try:
            if self.provider == "local":
                return self._local_chat(
                    messages,
                    json_mode,
                    temperature
                )

            return self._gemini_chat(
                messages,
                json_mode,
                temperature
            )

        except Exception as exc:
            traceback.print_exc()

            raise LLMUnavailable(
                f"{self.provider.capitalize()} request failed: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

    def _local_chat(self, messages, json_mode, temperature):

        kwargs = {
            "options": {
                "temperature": temperature,
                "num_ctx": OLLAMA_NUM_CTX
            }
        }

        if json_mode:
            kwargs["format"] = "json"

        response = self.client.chat(
            model=self.model,
            messages=messages,
            **kwargs
        )

        return response["message"]["content"]

    def _gemini_chat(self, messages, json_mode, temperature):

        system_instructions = []
        contents = []

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            if isinstance(content, list):
                content = "\n".join(
                    str(item) for item in content
                )

            content = str(content)

            if role == "system":
                system_instructions.append(content)
                continue

            if role in ("assistant", "model"):
                gemini_role = "model"
            else:
                gemini_role = "user"

            contents.append({
                "role": gemini_role,
                "parts": [{"text": content}]
            })

        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction="\n\n".join(system_instructions)
            if system_instructions else None,
            response_mime_type="application/json"
            if json_mode else "text"
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config
        )

        if not response.text:
            raise LLMUnavailable(
                "Gemini returned an empty response."
            )

        return response.text


llm = LLM()
