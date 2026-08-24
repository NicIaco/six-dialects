"""Minimal client for any OpenAI-compatible chat endpoint.

No SDK, no vendor. If it speaks /v1/chat/completions, it works: Apertus behind
Swisscom or CSCS, a local llama.cpp server, OpenAI, anything.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from . import __version__

USER_AGENT = f"six-dialects/{__version__}"


class EndpointError(RuntimeError):
    pass


@dataclass
class Endpoint:
    base_url: str
    model: str
    api_key: str = ""
    timeout: int = 120

    def chat(self, prompt: str, system: str | None = None,
             temperature: float = 0.0, max_tokens: int = 800) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        url = self.base_url.rstrip("/") + "/chat/completions"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                # some gateways (Public AI among them) reject the default
                # urllib agent as bot traffic
                "User-Agent": USER_AGENT,
                **({"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}),
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise EndpointError(f"{exc.code} from {url}: {exc.read()[:400]!r}") from exc
        except urllib.error.URLError as exc:
            raise EndpointError(f"could not reach {url}: {exc.reason}") from exc

        try:
            return body["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise EndpointError(f"unexpected response shape: {body}") from exc
