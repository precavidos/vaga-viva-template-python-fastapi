from datetime import datetime

import pytest

from app.appointments.duration import appointment_duration
from tests.support.dates import CLINIC_ZONE

pytestmark = pytest.mark.mission("bug-hunt")


def local(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=CLINIC_ZONE)


def test_calcula_a_duracao_de_uma_consulta_que_termina_no_dia_seguinte():
    minutes = appointment_duration(local("2030-03-04T23:30"), local("2030-03-05T00:30"))

    assert minutes == 60, f"esperava 60 minutos entre 23:30 e 00:30 do dia seguinte; recebeu {minutes}"


def test_calcula_a_duracao_de_um_plantao_noturno_de_varias_horas():
    minutes = appointment_duration(local("2030-03-04T22:00"), local("2030-03-05T02:15"))

    assert minutes == 255, f"esperava 255 minutos entre 22:00 e 02:15 do dia seguinte; recebeu {minutes}"


def test_calcula_a_duracao_de_um_periodo_de_exatamente_24_horas():
    minutes = appointment_duration(local("2030-03-04T10:00"), local("2030-03-05T10:00"))

    assert minutes == 1440, f"esperava 1440 minutos em 24 horas; recebeu {minutes}"


def test_calcula_a_duracao_na_virada_do_ano():
    minutes = appointment_duration(local("2030-12-31T23:45"), local("2031-01-01T00:15"))

    assert minutes == 30, f"esperava 30 minutos entre 23:45 de 31/12 e 00:15 de 01/01; recebeu {minutes}"
