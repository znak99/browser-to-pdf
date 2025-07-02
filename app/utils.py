from __future__ import annotations

import re
from urllib.parse import urlparse

ALLOWED_SCHEMES = {"http", "https"}


def normalize_target_url(raw_url: str) -> str:
    candidate = raw_url.strip()
    if not candidate:
        raise ValueError("변환할 URL을 입력하세요.")

    if "://" not in candidate:
        candidate = f"https://{candidate}"

    parsed = urlparse(candidate)
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise ValueError("http 또는 https URL만 사용할 수 있습니다.")

    if not parsed.netloc:
        raise ValueError("올바른 호스트가 포함된 URL을 입력하세요.")

    return candidate


def build_download_filename(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.")
    stem = re.sub(r"[^a-z0-9]+", "-", host).strip("-") or "website"
    return f"{stem}.pdf"
