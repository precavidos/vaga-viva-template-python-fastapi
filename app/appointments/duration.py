from datetime import datetime


def appointment_duration(start: datetime, end: datetime) -> int:
    """Duração, em minutos, entre o início e o fim de uma consulta."""
    start_minutes = start.hour * 60 + start.minute
    end_minutes = end.hour * 60 + end.minute
    return end_minutes - start_minutes
