"""Legacy — environment configuration."""
import os
import socket
from pathlib import Path

from dotenv import load_dotenv

# Primary: project-root .env. Fallback: ~/Downloads/env (user keeps keys there).
load_dotenv(Path(__file__).resolve().parents[2] / ".env")
if "COGNEE_API_KEY" not in os.environ:
    load_dotenv(Path.home() / "Downloads" / "env")

COGNEE_API_KEY = os.environ["COGNEE_API_KEY"]
COGNEE_BASE_URL = os.environ["COGNEE_BASE_URL"].rstrip("/")
COGNEE_HOST = COGNEE_BASE_URL.removeprefix("https://")
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
CME_MODEL = os.environ.get("CME_MODEL", "claude-haiku-4-5")

DATASET_NAME = os.environ.get("LEGACY_DATASET", "legacy_user_shanks")
NODE_SET = ["legacy_nodes"]

# The tenant is freshly provisioned and its DNS record hasn't propagated to
# every resolver yet. If the system resolver can't find it, fall back to a
# pinned IP (TLS still validates against the hostname via SNI).
_PINNED_IPS = {COGNEE_HOST: "54.197.228.131"}
_orig_getaddrinfo = socket.getaddrinfo


def _getaddrinfo_with_pin(host, *args, **kwargs):
    try:
        return _orig_getaddrinfo(host, *args, **kwargs)
    except socket.gaierror:
        if host in _PINNED_IPS:
            return _orig_getaddrinfo(_PINNED_IPS[host], *args, **kwargs)
        raise


socket.getaddrinfo = _getaddrinfo_with_pin


def parse_structured(response, key: str):
    """Extract and parse a structured-output JSON response defensively.
    Raises RuntimeError with a clear message on refusal/truncation."""
    import json as _json
    text = next((b.text for b in response.content if b.type == "text"), "")
    if not text:
        raise RuntimeError("model returned no output (possibly refused) — try again")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("model output was truncated — try again")
    try:
        return _json.loads(text)[key]
    except (ValueError, KeyError) as e:
        raise RuntimeError(f"model returned malformed output — try again ({e})") from e
