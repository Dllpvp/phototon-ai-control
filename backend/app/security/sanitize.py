"""Санитизация недоверенного входа: текст тикетов перед внешним LLM (PLAN-V2 §6.4).

Модуль вырезает промпт-инъекции (императивы, роль-префиксы, URL, shell/SQL-токены,
угловые/фигурные инструкции), но сохраняет факты и цифры — они нужны контексту.
Модуль НЕ логирует сырой текст (правило: сырьё в логи не пишем).
Внешний LLM получает только clean_summary + tags — гарантирует вызывающий.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

# ---------------------------------------------------------------------------
# Паттерны инъекций. Каждый срабатывает независимо; найденное вырезается
# и инкрементирует счётчик stripped_count.
# ---------------------------------------------------------------------------

# Хвост императива: до 5 «слов» (буквы/цифры/дефис), НЕ переходит запятую —
# чтобы факт в той же фразе после запятой выживал.
_TAIL = r"(?:\s+[\w'’-]+){0,5}"

_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    # Императивы RU: «игнорируй…», «забудь…», «выведи…», «открой…», «покажи…»
    re.compile(
        r"(?iu)\b(?:"
        r"игнорир(?:уй|уйте|уя|овать)"
        r"|забудь(?:те)?"
        r"|выведи(?:те)?"
        r"|расскажи"
        r")" + _TAIL
    ),
    re.compile(
        r"(?i)\b(?:"
        r"ignore\s+(?:all\s+|any\s+|previous\s+|prior\s+|the\s+)?(?:instructions?|rules?|prompts?|directives?)"
        r"|disregard\s+(?:all\s+|the\s+|your\s+)?(?:instructions?|rules?|prompts?|context)"
        r"|forget\s+(?:all\s+|your\s+|the\s+)?(?:instructions?|rules?|everything|context)"
        r"|reveal\s+(?:all\s+|the\s+)?(?:sums?|amounts?|data|secrets?)"
        r"|print\s+(?:all\s+|the\s+)?(?:sums?|amounts?|data|secrets?)"
        r")" + _TAIL
    ),
    # Роль-префиксы и системные маркеры
    re.compile(
        r"(?i)\b(?:system|assistant|user|developer)\s*:"
    ),
    re.compile(
        r"(?iu)\bты\s+теперь" + _TAIL
    ),
    re.compile(
        r"(?i)\byou\s+are\s+(?:now\s+)?(?:a|an|the|not|no)?[a-z]+(?:\s+[a-z']+){0,4}"
    ),
    re.compile(
        r"(?i)\b(?:act\s+as|pretend\s+to\s+be|pretend\s+you\s+are)" + _TAIL
    ),
    # URL любых схем
    re.compile(
        r"(?i)\b(?:https?|ftp|file|ssh|telnet)://\S+"
        r"|\bwww\.[^\s]+"
    ),
    # Shell/SQL-подобные токены
    re.compile(
        r"(?i)\b(?:"
        r"rm\s+-rf\s*\S*"
        r"|sudo"
        r"|drop\s+table"
        r"|delete\s+from"
        r"|insert\s+into"
        r"|union\s+(?:all\s+)?select"
        r"|\bxp_cmdshell\b"
        r"|\bexec(?:ute)?\s+shell"
        r")" + _TAIL
    ),
    # Угловые/фигурные «инструкции»: <tag>…</tag>, {command}, [[directive]]
    re.compile(
        r"<[/a-zA-Z][^<>]{0,200}>(?:[\s\S]{0,400}?</[/a-zA-Z][^<>]{0,200}>)?"
    ),
    re.compile(
        r"\{[a-zA-Z_][^{}\n]{0,200}\}"
    ),
    re.compile(
        r"\[\[[^\]\n]{1,200}\]\]"
    ),
]

# Стоп-фразы (целиком), которых нет в регэкспах выше.
_STOP_PHRASES: list[str] = [
    "you are now",
    "ты теперь другой ассистент",
    "забудь инструкции",
    "забудь все инструкции",
    "игнорируй правила",
    "system:",
    "игнорируй предыдущие инструкции",
]


def sanitize_ticket(
    text: str,
    allowed_tags: Sequence[str] | None = None,
) -> dict:
    """Санитизировать текст тикета.

    Возвращает словарь:
      - "tags": теги из allowed_tags, найденные в тексте (word-boundary).
        При allowed_tags=None — пустой список (справочник тегов передаёт T10).
      - "clean_summary": текст с вырезанными инъекциями.
      - "stripped_count": количество вырезанных фрагментов.

    Факты и цифры сохраняются: они нужны контексту. Сырой текст в LLM не
    попадает никогда — вызывающий кладёт в ctx только clean_summary + tags.
    Модуль ничего не логирует (в т.ч. сырьё).
    """
    if not text:
        return {"tags": [], "clean_summary": text, "stripped_count": 0}

    stripped_count = 0
    working = text

    for pattern in _INJECTION_PATTERNS:
        while True:
            new_value, count = pattern.subn("", working)
            stripped_count += count
            working = new_value
            if count == 0:
                break

    lower = working.casefold()
    for phrase in _STOP_PHRASES:
        while True:
            idx = lower.find(phrase.casefold())
            if idx == -1:
                break
            # вырезаем фразу и прибираем образующийся двойной пробел
            working = working[:idx] + working[idx + len(phrase):]
            stripped_count += 1
            lower = working.casefold()

    working = _squeeze_spaces(working)

    tags = _extract_tags(working, allowed_tags)

    return {
        "tags": tags,
        "clean_summary": working.strip(),
        "stripped_count": stripped_count,
    }


def _squeeze_spaces(text: str) -> str:
    """Схлопнуть дубли пробелов и подчистить хвосты знаков препинания."""
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    text = re.sub(r"([,.!?;:])(?=[А-Яа-яЁёA-Za-z])", r"\1 ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def _extract_tags(
    text: str,
    allowed_tags: Sequence[str] | None,
) -> list[str]:
    """Найти разрешённые теги в тексте; порядок — как в allowed_tags."""
    if not allowed_tags:
        return []
    found: list[str] = []
    for tag in allowed_tags:
        if not tag:
            continue
        if re.search(r"(?<![\w-])" + re.escape(tag) + r"(?![\w-])", text):
            found.append(tag)
    return found


__all__ = ["sanitize_ticket"]
