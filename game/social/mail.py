from __future__ import annotations

from datetime import datetime
from typing import Any, Optional


def create_mail(
    sender_id: int,
    sender_name: str,
    recipient_id: int,
    subject: str,
    content: str,
    gold_attached: int = 0,
    items_attached: Optional[list[str]] = None,
) -> dict[str, Any]:
    return {
        "sender_id": sender_id,
        "sender_name": sender_name,
        "recipient_id": recipient_id,
        "subject": subject,
        "content": content,
        "gold_attached": gold_attached,
        "items_attached": items_attached or [],
        "is_read": False,
        "created_at": datetime.utcnow().isoformat(),
    }


def validate_mail(subject: str, content: str) -> Optional[str]:
    if not subject or len(subject) > 100:
        return "Тема письма должна быть от 1 до 100 символов."
    if not content or len(content) > 1000:
        return "Текст письма должен быть от 1 до 1000 символов."
    return None


def format_mail(mail: Any) -> str:
    read_status = "📭" if not mail.is_read else "📬"
    lines = [
        f"{read_status} <b>{mail.subject}</b>",
        f"👤 От: {mail.sender_name}",
        f"📝 {mail.content}",
    ]
    if mail.gold_attached and mail.gold_attached > 0:
        lines.append(f"💰 Вложение: {mail.gold_attached} золота")
    items = mail.items_attached if mail.items_attached else []
    if items:
        lines.append(f"📦 Предметы: {', '.join(items)}")
    if mail.created_at:
        ts = mail.created_at.strftime("%d.%m.%Y %H:%M") if hasattr(mail.created_at, "strftime") else str(mail.created_at)
        lines.append(f"🕐 {ts}")
    return "\n".join(lines)


def format_mailbox(mails: list[Any]) -> str:
    if not mails:
        return "📬 Почтовый ящик пуст."
    unread = sum(1 for m in mails if not m.is_read)
    lines = [f"📬 <b>Почта ({unread} непрочитанных):</b>", ""]
    for i, mail in enumerate(mails[:20], 1):
        read_icon = "🔵" if not mail.is_read else "⚪"
        lines.append(f"  {read_icon} {i}. {mail.subject} — от {mail.sender_name}")
    return "\n".join(lines)
