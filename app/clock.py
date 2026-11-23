from datetime import datetime
from typing import Annotated, Protocol
from zoneinfo import ZoneInfo

from fastapi import Depends

from app.config import Settings, get_settings


class Clock(Protocol):
    """Relógio da aplicação: devolve o momento atual no fuso da clínica."""

    def now(self) -> datetime: ...


class SystemClock:
    def __init__(self, zone: ZoneInfo) -> None:
        self._zone = zone

    def now(self) -> datetime:
        return datetime.now(self._zone)


def get_clock(settings: Annotated[Settings, Depends(get_settings)]) -> Clock:
    """Dependência do FastAPI que fornece o relógio (`Depends(get_clock)`)."""
    return SystemClock(settings.zone)
