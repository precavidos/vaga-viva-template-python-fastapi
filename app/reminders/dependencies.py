from typing import Annotated

from fastapi import Depends

from app.reminders.senders import EmailSender, LoggingEmailSender, LoggingSmsSender, SmsSender
from app.reminders.strategy import ReminderStrategy


def get_email_sender() -> EmailSender:
    return LoggingEmailSender()


def get_sms_sender() -> SmsSender:
    return LoggingSmsSender()


def get_reminder_strategies(
    email_sender: Annotated[EmailSender, Depends(get_email_sender)],
    sms_sender: Annotated[SmsSender, Depends(get_sms_sender)],
) -> list[ReminderStrategy]:
    """As estratégias de lembrete, uma por canal."""
    return []
