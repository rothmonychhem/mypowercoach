from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import error, request


@dataclass(frozen=True, slots=True)
class LlmChatConfig:
    provider: str
    timeout_seconds: float
    max_output_tokens: int
    ollama_base_url: str
    ollama_model: str
    ollama_api_key: str
    gemini_api_key: str
    gemini_model: str
    groq_api_key: str
    groq_model: str


class LlmChatClient:
    def __init__(self, config: LlmChatConfig) -> None:
        self._config = config

    @property
    def enabled(self) -> bool:
        provider = self._config.provider
        if provider == "ollama":
            return bool(self._config.ollama_model and self._config.ollama_base_url)
        if provider == "gemini":
            return bool(self._config.gemini_api_key and self._config.gemini_model)
        if provider == "groq":
            return bool(self._config.groq_api_key and self._config.groq_model)
        return False

    def generate(self, system_prompt: str, user_prompt: str) -> str | None:
        if not self.enabled:
            return None

        try:
            if self._config.provider == "ollama":
                return self._generate_ollama(system_prompt, user_prompt)
            if self._config.provider == "gemini":
                return self._generate_gemini(system_prompt, user_prompt)
            if self._config.provider == "groq":
                return self._generate_groq(system_prompt, user_prompt)
        except (TimeoutError, ValueError, error.URLError, error.HTTPError, OSError):
            return None

        return None

    def _generate_ollama(self, system_prompt: str, user_prompt: str) -> str | None:
        payload = {
            "model": self._config.ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        }
        headers = {"Content-Type": "application/json"}
        if self._config.ollama_api_key:
            headers["Authorization"] = f"Bearer {self._config.ollama_api_key}"
        data = self._post_json(f"{self._config.ollama_base_url.rstrip('/')}/chat", payload, headers=headers)
        message = data.get("message", {})
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
        return None

    def _generate_gemini(self, system_prompt: str, user_prompt: str) -> str | None:
        model = self._config.gemini_model
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            f"?key={self._config.gemini_api_key}"
        )
        payload = {
            "systemInstruction": {
                "parts": [{"text": system_prompt}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.5,
                "topP": 0.9,
                "maxOutputTokens": self._config.max_output_tokens,
            },
        }
        data = self._post_json(url, payload, headers={"Content-Type": "application/json"})
        candidates = data.get("candidates", [])
        if not candidates:
            return None
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        texts = [part.get("text", "").strip() for part in parts if part.get("text")]
        joined = "\n".join(texts).strip()
        return joined or None

    def _generate_groq(self, system_prompt: str, user_prompt: str) -> str | None:
        payload = {
            "model": self._config.groq_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.5,
            "max_tokens": self._config.max_output_tokens,
        }
        data = self._post_json(
            "https://api.groq.com/openai/v1/chat/completions",
            payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._config.groq_api_key}",
            },
        )
        choices = data.get("choices", [])
        if not choices:
            return None
        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
        return None

    def _post_json(self, url: str, payload: dict, headers: dict[str, str]) -> dict:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(url, data=body, headers=headers, method="POST")
        with request.urlopen(req, timeout=self._config.timeout_seconds) as response:
            raw = response.read().decode("utf-8")
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("Unexpected LLM response payload.")
        return data
