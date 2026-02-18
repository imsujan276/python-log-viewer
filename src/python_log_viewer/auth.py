"""
HTTP Basic Authentication helpers (stdlib only).
"""

from __future__ import annotations

import base64
import secrets
from typing import Optional, Tuple


def decode_basic_auth(header_value: str) -> Optional[Tuple[str, str]]:
    """Decode an ``Authorization: Basic ...`` header.

    Returns ``(username, password)`` or ``None`` on failure.
    """
    if not header_value.startswith("Basic "):
        return None
    try:
        decoded = base64.b64decode(header_value[6:]).decode("utf-8")
        username, password = decoded.split(":", 1)
        return username, password
    except Exception:
        return None


def check_credentials(
    header_value: str,
    expected_username: str,
    expected_password: str,
) -> bool:
    """Verify Basic-Auth credentials using constant-time comparison."""
    creds = decode_basic_auth(header_value)
    if creds is None:
        return False
    username, password = creds
    return secrets.compare_digest(username, expected_username) and secrets.compare_digest(
        password, expected_password
    )
