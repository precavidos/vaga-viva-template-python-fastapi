from datetime import time
from enum import StrEnum
from functools import lru_cache
from typing import Annotated
from zoneinfo import ZoneInfo

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode


class Weekday(StrEnum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"

    @property
    def iso_number(self) -> int:
        """1 para segunda-feira, 7 para domingo, como em `date.isoweekday()`."""
        return list(Weekday).index(self) + 1


class Settings(BaseSettings):
    """Configuração da aplicação, lida das variáveis de ambiente (por exemplo, `CLINIC_TIME_ZONE`)."""

    database_url: str = "postgresql://clinic:clinic@localhost:5432/clinic"
    clinic_time_zone: str = "America/Sao_Paulo"
    clinic_opening_days: Annotated[list[Weekday], NoDecode] = [
        Weekday.MONDAY,
        Weekday.TUESDAY,
        Weekday.WEDNESDAY,
        Weekday.THURSDAY,
        Weekday.FRIDAY,
    ]
    clinic_opens_at: time = time(8, 0)
    clinic_closes_at: time = time(18, 0)

    @field_validator("clinic_opening_days", mode="before")
    @classmethod
    def _split_days(cls, value: object) -> object:
        if isinstance(value, str):
            days = [day.strip().upper() for day in value.split(",") if day.strip()]
            unknown = [day for day in days if day not in Weekday.__members__]
            if unknown:
                raise ValueError(
                    f"CLINIC_OPENING_DAYS: dia da semana desconhecido '{unknown[0]}'. Use {', '.join(Weekday)}."
                )
            return days
        return value

    @property
    def zone(self) -> ZoneInfo:
        return ZoneInfo(self.clinic_time_zone)


@lru_cache
def get_settings() -> Settings:
    return Settings()
