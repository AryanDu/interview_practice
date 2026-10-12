"""Small helpers for safely rendering untrusted text and filenames."""
from __future__ import annotations

from html import escape
import re
from typing import Any


def escape_html_text(value: Any, *, max_length: int = 12000) -> str:
    """Escape dynamic text before embedding it inside explicitly trusted HTML."""
    text = str(value if value is not None else "").replace("\x00", "")
    return escape(text[:max(0, max_length)], quote=True)


def safe_filename_component(value: Any, *, max_length: int = 60) -> str:
    """Return a short filename component without paths, control chars or extension tricks."""
    text = str(value if value is not None else "").replace("\x00", "")
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", text).strip("._-")
    return (cleaned[:max(1, max_length)] or "download")
