"""Mask sensitive identities and money before leaving the trusted perimeter."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

SENSITIVE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "EMP",
        re.compile(
            r"(?<![А-Яа-яЁё])"
            r"[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+"
            r"(?:\s+[А-ЯЁ][а-яё]+)?"
            r"(?![А-Яа-яЁё])"
        ),
    ),
    (
        "CLIENT",
        re.compile(
            r"«[^»\n]+»"
            r"|\bКлиент\s*№\s*\d+\b"
            r"|\bB2B\s+[А-ЯЁA-Z0-9][\wА-Яа-яЁё-]*(?:\s+[А-ЯЁA-Z0-9][\wА-Яа-яЁё-]*)*",
            re.IGNORECASE,
        ),
    ),
]
MONEY_KEY_REGEX = re.compile(
    r"(?:^|_)(?:amount|amount_byn|sum|total|cost|revenue|turnover|price|money|loss|refund|margin)(?:_|$)|byn",
    re.IGNORECASE,
)
_MONEY_VALUE_REGEX = re.compile(
    r"(?<![\w])(?:\d{1,3}(?:[ \u00a0]\d{3})+|\d+)(?:[,.]\d{1,2})?\s*BYN\b",
    re.IGNORECASE,
)
_TOKEN_REGEX = re.compile(r"\[(?:EMP|CLIENT|AMT)_\d+\]")


def mask(ctx: dict, level: str = "strict") -> tuple[dict, dict]:
    """Return a recursively masked copy and a per-call token-to-value vault."""
    if level not in {"strict", "standard"}:
        raise ValueError("level must be 'strict' or 'standard'")

    vault: dict[str, str] = {}
    tokens: dict[tuple[str, str], str] = {}
    counts = {"EMP": 0, "CLIENT": 0, "AMT": 0}

    def replace_entity(kind: str, value: str) -> str:
        key = (kind, value)
        if key not in tokens:
            counts[kind] += 1
            token = f"[{kind}_{counts[kind]:02d}]"
            tokens[key] = token
            vault[token] = value
        return tokens[key]

    def mask_string(value: str, money_key: bool = False) -> str:
        if level == "strict":
            if money_key:
                value = _mask_money_text(value, replace_entity)
            else:
                value = _MONEY_VALUE_REGEX.sub(
                    lambda match: replace_entity("AMT", match.group(0)), value
                )

        for kind, pattern in SENSITIVE_PATTERNS:
            value = pattern.sub(
                lambda match, entity_kind=kind: replace_entity(
                    entity_kind, match.group(0)
                ),
                value,
            )
        return value

    def walk(value: Any, key: Any = None) -> Any:
        money_key = isinstance(key, str) and bool(MONEY_KEY_REGEX.search(key))
        if isinstance(value, str):
            if level == "strict" and money_key:
                return _mask_money_text(value, replace_entity)
            return mask_string(value)
        if isinstance(value, Mapping):
            return {
                item_key: walk(item_value, item_key)
                for item_key, item_value in value.items()
            }
        if isinstance(value, list):
            return [walk(item, key) for item in value]
        if isinstance(value, tuple):
            return tuple(walk(item, key) for item in value)
        if level == "strict" and money_key and isinstance(value, (int, float)) and not isinstance(value, bool):
            return replace_entity("AMT", str(value))
        return value

    return walk(ctx), vault


def _mask_money_text(value: str, replace_entity: Any) -> str:
    return _MONEY_VALUE_REGEX.sub(
        lambda match: replace_entity("AMT", match.group(0)), value
    )


def detokenize(text: str, vault: dict) -> str:
    """Restore known tokens in text using the request-local vault."""
    for token in sorted(vault, key=len, reverse=True):
        text = text.replace(token, vault[token])
    return text
