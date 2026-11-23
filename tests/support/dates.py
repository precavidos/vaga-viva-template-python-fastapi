"""Datas relativas ao relógio real, no fuso da clínica. Datas no formato `AAAA-MM-DD` e datas e horas locais no formato
`AAAA-MM-DDTHH:MM:SS`, sem fuso."""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

CLINIC_ZONE = ZoneInfo("America/Sao_Paulo")

MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = range(1, 8)

_LOCAL_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _today() -> date:
    return datetime.now(CLINIC_ZONE).date()


def future_date(weekday: int) -> str:
    """Primeiro dia da semana pedido (1 = segunda, 7 = domingo) que esteja pelo menos 7 dias no futuro."""
    base = _today() + timedelta(days=7)
    return (base + timedelta(days=(weekday - base.isoweekday()) % 7)).isoformat()


def past_date(weekday: int) -> str:
    """Dia da semana pedido, pelo menos 7 dias no passado."""
    base = _today() - timedelta(days=7)
    return (base - timedelta(days=(base.isoweekday() - weekday) % 7)).isoformat()


def plus_days(day: str, days: int) -> str:
    return (date.fromisoformat(day) + timedelta(days=days)).isoformat()


def at(day: str, time: str) -> str:
    return f"{day}T{time}:00"


def plus_minutes(date_time: str, minutes: int) -> str:
    return (datetime.fromisoformat(date_time) + timedelta(minutes=minutes)).strftime(_LOCAL_FORMAT)


def local_date_time(value: object) -> object:
    """Normaliza uma data e hora da resposta da API para `AAAA-MM-DDTHH:MM:SS`, para comparar com o valor esperado.
    Devolve o valor original quando ele não é uma data e hora ISO, para o teste falhar com uma mensagem clara."""
    if not isinstance(value, str):
        return value
    try:
        return datetime.fromisoformat(value).strftime(_LOCAL_FORMAT)
    except ValueError:
        return value
