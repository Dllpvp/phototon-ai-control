"""Telegram-бот: отправка уведомлений с фолбэком (§4.4 Readme.md).

Правила:
- Если `settings.telegram_bot_token` пуст ИЛИ `settings.offline_mode=True`
  → возвращаем `Notification(status="skipped_no_token")`, HTTP НЕ делаем.
- Если токен есть → httpx.post с таймаутом 3 с, оборачиваем в try/except.
- **НИКОГДА не бросаем исключение наружу.** В случае ошибки возвращаем
  `Notification(status="failed")`.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime

import httpx

from app.config import settings
from app.schemas import NotificationDTO

logger = logging.getLogger(__name__)

_TELEGRAM_TIMEOUT = 3.0  # секунд


def send_message(
    chat_id: str,
    text: str,
    subject: str = "Фотопринт·Контроль",
    related_decision_id: str | None = None,
) -> NotificationDTO:
    """Отправляет сообщение в Telegram. Безопасна: никогда не бросает исключение.

    Возвращает NotificationDTO со статусом sent / failed / skipped_no_token.
    """
    token = settings.telegram_bot_token
    if not token or settings.offline_mode:
        return NotificationDTO(
            id=str(uuid.uuid4()),
            channel="telegram",
            recipient=chat_id or settings.telegram_chat_id or "",
            subject=subject,
            body=text,
            status="skipped_no_token",
            created_at=datetime.now(),
            related_decision_id=related_decision_id,
        )

    recipient = chat_id or settings.telegram_chat_id
    if not recipient:
        return NotificationDTO(
            id=str(uuid.uuid4()),
            channel="telegram",
            recipient="",
            subject=subject,
            body=text,
            status="skipped_no_token",
            created_at=datetime.now(),
        )

    url = f"{settings.telegram_api_base}/bot{token}/sendMessage"
    payload = {"chat_id": recipient, "text": text, "parse_mode": "HTML"}

    try:
        with httpx.Client(timeout=_TELEGRAM_TIMEOUT) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                return NotificationDTO(
                    id=str(uuid.uuid4()),
                    channel="telegram",
                    recipient=recipient,
                    subject=subject,
                    body=text,
                    status="sent",
                    created_at=datetime.now(),
                )
            logger.warning("Telegram API вернул %s: %s", resp.status_code, resp.text[:200])
            return NotificationDTO(
                id=str(uuid.uuid4()),
                channel="telegram",
                recipient=recipient,
                subject=subject,
                body=text,
                status="failed",
                created_at=datetime.now(),
            )
    except Exception as exc:
        logger.warning("Telegram send failed: %s", exc)
        return NotificationDTO(
            id=str(uuid.uuid4()),
            channel="telegram",
            recipient=recipient,
            subject=subject,
            body=text,
            status="failed",
            created_at=datetime.now(),
        )
