import pytest

from tests.support.api import Api, expect_status
from tests.support.database import Database
from tests.support.dates import MONDAY, SATURDAY, SUNDAY, at, future_date, local_date_time, plus_days

pytestmark = pytest.mark.mission("availability-query")

PATIENT_ID = 1
MONDAY_DATE = future_date(MONDAY)


def slot(day: str, start: str, end: str) -> dict[str, object]:
    return {"start": at(day, start), "end": at(day, end)}


@pytest.fixture
def professional_id(db: Database) -> int:
    return db.insert_professional()


def availability(api: Api, professional: int, day: str) -> list[dict[str, object]]:
    response = api.get(f"/professionals/{professional}/availability?date={day}")
    expect_status(response, 200, f"esperava status 200 em GET /professionals/{{id}}/availability?date={day}")
    assert isinstance(response.body, list) and all(isinstance(item, dict) for item in response.body), (
        f"esperava uma lista JSON de intervalos {{start, end}}; {response.describe()}"
    )
    return [
        {"start": local_date_time(item.get("start")), "end": local_date_time(item.get("end"))} for item in response.body
    ]


def test_um_dia_util_sem_consultas_fica_livre_das_08_00_as_18_00(api, professional_id):
    free = availability(api, professional_id, MONDAY_DATE)

    assert free == [slot(MONDAY_DATE, "08:00", "18:00")], (
        f"esperava um único intervalo livre das 08:00 às 18:00; recebeu {free}"
    )


def test_devolve_os_intervalos_entre_as_consultas_em_ordem(api, db, professional_id):
    db.insert_appointment(professional_id, PATIENT_ID, at(MONDAY_DATE, "13:00"), 90)
    db.insert_appointment(professional_id, PATIENT_ID, at(MONDAY_DATE, "09:00"), 60)

    free = availability(api, professional_id, MONDAY_DATE)

    assert free == [
        slot(MONDAY_DATE, "08:00", "09:00"),
        slot(MONDAY_DATE, "10:00", "13:00"),
        slot(MONDAY_DATE, "14:30", "18:00"),
    ], f"esperava os intervalos livres 08:00-09:00, 10:00-13:00 e 14:30-18:00; recebeu {free}"


def test_ignora_consultas_de_outros_profissionais_e_de_outros_dias(api, db, professional_id):
    other_professional_id = db.insert_professional("Dr. Rafael Moura", "Cardiologia")
    db.insert_appointment(other_professional_id, PATIENT_ID, at(MONDAY_DATE, "10:00"), 60)
    db.insert_appointment(professional_id, PATIENT_ID, at(plus_days(MONDAY_DATE, 1), "10:00"), 60)
    db.insert_appointment(professional_id, PATIENT_ID, at(MONDAY_DATE, "15:00"), 30)

    free = availability(api, professional_id, MONDAY_DATE)

    assert free == [slot(MONDAY_DATE, "08:00", "15:00"), slot(MONDAY_DATE, "15:30", "18:00")], (
        f"esperava só a consulta das 15:00 do próprio profissional, nesse dia, ocupando a agenda; recebeu {free}"
    )


def test_nao_devolve_intervalos_vazios_entre_consultas_encostadas_nem_nas_pontas_do_dia(api, db, professional_id):
    db.insert_appointment(professional_id, PATIENT_ID, at(MONDAY_DATE, "08:00"), 60)
    db.insert_appointment(professional_id, PATIENT_ID, at(MONDAY_DATE, "09:00"), 60)
    db.insert_appointment(professional_id, PATIENT_ID, at(MONDAY_DATE, "17:00"), 60)

    free = availability(api, professional_id, MONDAY_DATE)

    assert free == [slot(MONDAY_DATE, "10:00", "17:00")], (
        f"esperava só o intervalo livre das 10:00 às 17:00; recebeu {free}"
    )


def test_nao_ha_horarios_livres_no_fim_de_semana(api, professional_id):
    assert availability(api, professional_id, future_date(SATURDAY)) == [], "esperava lista vazia no sábado"
    assert availability(api, professional_id, future_date(SUNDAY)) == [], "esperava lista vazia no domingo"
