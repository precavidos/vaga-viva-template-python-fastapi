import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class EmailSender(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...


class SmsSender(Protocol):
    def send(self, phone: str, text: str) -> None: ...


class LoggingEmailSender:
    def send(self, to: str, subject: str, body: str) -> None:
        logger.info("E-mail para %s: %s - %s", to, subject, body)


class LoggingSmsSender:
    def send(self, phone: str, text: str) -> None:
        logger.info("SMS para %s: %s", phone, text)
