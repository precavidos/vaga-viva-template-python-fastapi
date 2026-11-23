from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class ReminderChannel(StrEnum):
    EMAIL = "EMAIL"
    SMS = "SMS"


@dataclass(frozen=True)
class Reminder:
    patient_name: str
    patient_email: str
    patient_phone: str
    professional_name: str
    start: datetime
