"""Shared field helpers for schemas."""

from __future__ import annotations


def normalize_country_code(value: str) -> str:
    code = value.strip().upper()
    if len(code) != 2 or not code.isalpha():
        raise ValueError("must be a 2-letter ISO country code")
    return code
