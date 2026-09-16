from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from uuid import uuid4


DEFAULT_WARPBLACK_URL = "http://127.0.0.1:8765"
TOKEN_ENV = "WARPBLACK_TOKEN"
URL_ENV = "WARPBLACK_URL"
TIMEOUT_ENV = "WARPBLACK_HTTP_TIMEOUT_S"


class WarpBlackError(RuntimeError):
    """Base error for the XarvisCore <-> WARPBLACK transport."""


class WarpBlackConfigurationError(WarpBlackError):
    """Raised when the local bridge configuration is unsafe or incomplete."""


@dataclass(frozen=True)
class WarpBlackConfig:
    base_url: str = DEFAULT_WARPBLACK_URL
    token: str = ""
    http_timeout_s: float = 70.0

    @classmethod
    def from_env(cls) -> "WarpBlackConfig":
        token = os.environ.get(TOKEN_ENV, "").strip()
        if not token:
            raise WarpBlackConfigurationError(f"{TOKEN_ENV} is required")

        raw_timeout = os.environ.get(TIMEOUT_ENV, "70").strip()
        try:
            http_timeout_s = float(raw_timeout)
        except ValueError as exc:
            raise WarpBlackConfigurationError(
                f"{TIMEOUT_ENV} must be numeric"
            ) from exc
        if http_timeout_s <= 0:
            raise WarpBlackConfigurationError(f"{TIMEOUT_ENV} must be positive")

        return cls(
            base_url=os.environ.get(URL_ENV, DEFAULT_WARPBLACK_URL).strip(),
            token=token,
            http_timeout_s=http_timeout_s,
        )

    def validate(self) -> None:
        parsed = urlparse(self.base_url)
        if parsed.scheme != "http":
            raise WarpBlackConfigurationError(
                "direct WARPBLACK bridge must use local HTTP"
            )
        if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise WarpBlackConfigurationError(
                "direct WARPBLACK bridge must point to a loopback host"
            )
        if not self.token:
            raise WarpBlackConfigurationError(f"{TOKEN_ENV} is required")
        if self.http_timeout_s <= 0:
            raise WarpBlackConfigurationError("http_timeout_s must be positive")


class WarpBlackAdapter:
    """Protocol-v1 client used by XarvisCore to reach the local WARPBLACK bridge."""

    def __init__(self, config: WarpBlackConfig):
        config.validate()
        self.config = config
        self.base_url = config.base_url.rstrip("/")

    @classmethod
    def from_env(cls) -> "WarpBlackAdapter":
        return cls(WarpBlackConfig.from_env())

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/v1/health", authenticated=False)

    def capabilities(self) -> dict[str, Any]:
        return self._request("GET", "/v1/capabilities", authenticated=True)

    def execute(
        self,
        argv: Sequence[str],
        *,
        cwd: str = ".",
        timeout_s: float = 60.0,
        approved: bool = False,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        if isinstance(argv, (str, bytes)) or not argv:
            raise ValueError("argv must be a non-empty sequence of strings")
        if any(not isinstance(arg, str) or not arg for arg in argv):
            raise ValueError("argv entries must be non-empty strings")
        if timeout_s <= 0:
            raise ValueError("timeout_s must be positive")

        correlation_id = request_id or f"xarvis:{uuid4().hex}"
        payload = {
            "argv": list(argv),
            "cwd": cwd,
            "timeout_s": timeout_s,
            "approved": bool(approved),
            "request_id": correlation_id,
        }
        result = self._request(
            "POST",
            "/v1/execute",
            authenticated=True,
            payload=payload,
        )
        returned_id = result.get("request_id")
        if returned_id != correlation_id:
            raise WarpBlackError(
                "WARPBLACK request_id mismatch; refusing uncorrelated result"
            )
        return result

    def _request(
        self,
        method: str,
        path: str,
        *,
        authenticated: bool,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        data = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if authenticated:
            headers["Authorization"] = f"Bearer {self.config.token}"

        request = Request(
            f"{self.base_url}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with urlopen(request, timeout=self.config.http_timeout_s) as response:
                decoded = response.read().decode("utf-8")
        except HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                message = str(json.loads(raw).get("error", raw))
            except json.JSONDecodeError:
                message = raw or str(exc)
            raise WarpBlackError(
                f"WARPBLACK returned HTTP {exc.code}: {message}"
            ) from exc
        except URLError as exc:
            raise WarpBlackError(
                f"WARPBLACK bridge unavailable: {exc.reason}"
            ) from exc

        try:
            result = json.loads(decoded)
        except json.JSONDecodeError as exc:
            raise WarpBlackError("WARPBLACK returned invalid JSON") from exc
        if not isinstance(result, dict):
            raise WarpBlackError("WARPBLACK returned a non-object JSON response")
        return result
