from typing import Protocol

from app.reminders.reminder import Reminder, ReminderChannel


class ReminderStrategy(Protocol):
    """Contrato de um canal de lembrete."""

    @property
    def channel(self) -> ReminderChannel: ...

    def send(self, reminder: Reminder) -> None: ...
