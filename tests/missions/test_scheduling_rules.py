import pytest

from tests.support.api import Api, ApiResponse, expect_status
from tests.support.database import Database
from tests.support.dates import MONDAY, SATURDAY, at, future_date, local_date_time, past_date
from tests.support.patients import create_patient

pytestmark = pytest.mark.mission("scheduling-rules")

MONDAY_DATE = future_date(MONDAY)


class Scenario:
    """Um paciente, cadastrado pela API, e um profissional, gravado direto no banco."""

    def __init__(self, api: Api, db: Database) -> None:
        self.api = api
        self.patient_id = create_patient(api)
        self.professional_id = db.insert_professional()

    def schedule(self, professional: int, start: str, end: str) -> ApiResponse:
        return self.api.post(
            "/appointments", {"patientId": self.patient_id, "professionalId": professional, "start": start, "end": end}
        )


def test_agenda_uma_consulta_dentro_do_horario_de_funcionamento(api, db):
    scenario = Scenario(api, db)
    start = at(MONDAY_DATE, "10:00")
    end = at(MONDAY_DATE, "10:30")

    response = scenario.schedule(scenario.professional_id, start, end)

    expect_status(response, 201, "esperava status 201 em POST /appointments")
    appointment_id = response.json("id")
    assert isinstance(appointment_id, int), f"esperava o campo 'id' numérico na resposta; {response.describe()}"
    assert response.json("professionalId") == scenario.professional_id, "esperava o campo 'professionalId' na resposta"
    assert response.json("patientId") == scenario.patient_id, "esperava o campo 'patientId' na resposta"
    assert local_date_time(response.json("start")) == start, "esperava o campo 'start' na resposta"
    assert local_date_time(response.json("end")) == end, "esperava o campo 'end' na resposta"
    rows = db.query(
        "SELECT professional_id, patient_id, starts_at::text AS starts_at, duration_minutes "
        "FROM appointments WHERE id = %s",
        (appointment_id,),
    )
    assert rows == [
        {
            "professional_id": scenario.professional_id,
            "patient_id": scenario.patient_id,
            "starts_at": f"{MONDAY_DATE} 10:00:00",
            "duration_minutes": 30,
        }
    ], "esperava a consulta gravada na tabela appointments com duração de 30 minutos"


def test_recusa_com_422_uma_consulta_no_passado(api, db):
    scenario = Scenario(api, db)
    past_monday = past_date(MONDAY)

    response = scenario.schedule(scenario.professional_id, at(past_monday, "10:00"), at(past_monday, "10:30"))

    expect_status(response, 422, "esperava recusar consulta no passado com status 422")
    assert db.count_appointments() == 0, "esperava que a consulta recusada não fosse gravada"


def test_recusa_com_422_consultas_fora_do_horario_de_funcionamento(api, db):
    scenario = Scenario(api, db)
    saturday = future_date(SATURDAY)

    before_opening = scenario.schedule(scenario.professional_id, at(MONDAY_DATE, "07:30"), at(MONDAY_DATE, "08:30"))
    after_closing = scenario.schedule(scenario.professional_id, at(MONDAY_DATE, "17:30"), at(MONDAY_DATE, "18:30"))
    on_saturday = scenario.schedule(scenario.professional_id, at(saturday, "10:00"), at(saturday, "10:30"))

    expect_status(before_opening, 422, "esperava recusar com 422 consulta que começa antes das 08:00")
    expect_status(after_closing, 422, "esperava recusar com 422 consulta que termina depois das 18:00")
    expect_status(on_saturday, 422, "esperava recusar com 422 consulta no sábado")
    assert db.count_appointments() == 0, "esperava que as consultas recusadas não fossem gravadas"


def test_aceita_consultas_que_comecam_na_abertura_e_terminam_no_fechamento(api, db):
    scenario = Scenario(api, db)
    at_opening = scenario.schedule(scenario.professional_id, at(MONDAY_DATE, "08:00"), at(MONDAY_DATE, "08:30"))
    at_closing = scenario.schedule(scenario.professional_id, at(MONDAY_DATE, "17:30"), at(MONDAY_DATE, "18:00"))

    expect_status(at_opening, 201, "esperava aceitar consulta das 08:00 às 08:30")
    expect_status(at_closing, 201, "esperava aceitar consulta das 17:30 às 18:00")


def test_recusa_com_409_uma_consulta_que_se_sobrepoe_a_outra_do_mesmo_profissional(api, db):
    scenario = Scenario(api, db)
    db.insert_appointment(scenario.professional_id, scenario.patient_id, at(MONDAY_DATE, "10:00"), 60)

    overlaps_end = scenario.schedule(scenario.professional_id, at(MONDAY_DATE, "10:30"), at(MONDAY_DATE, "11:30"))
    overlaps_start = scenario.schedule(scenario.professional_id, at(MONDAY_DATE, "09:30"), at(MONDAY_DATE, "10:30"))
    contains = scenario.schedule(scenario.professional_id, at(MONDAY_DATE, "09:00"), at(MONDAY_DATE, "12:00"))

    expect_status(
        overlaps_end, 409, "esperava recusar com 409 consulta das 10:30 às 11:30 sobre outra das 10:00 às 11:00"
    )
    expect_status(
        overlaps_start, 409, "esperava recusar com 409 consulta das 09:30 às 10:30 sobre outra das 10:00 às 11:00"
    )
    expect_status(contains, 409, "esperava recusar com 409 consulta das 09:00 às 12:00 sobre outra das 10:00 às 11:00")
    assert db.count_appointments() == 1, "esperava que só a consulta original estivesse gravada"


def test_aceita_consultas_encostadas_e_consultas_no_mesmo_horario_com_outro_profissional(api, db):
    scenario = Scenario(api, db)
    other_professional_id = db.insert_professional("Dr. Rafael Moura", "Cardiologia")
    db.insert_appointment(scenario.professional_id, scenario.patient_id, at(MONDAY_DATE, "10:00"), 60)

    after = scenario.schedule(scenario.professional_id, at(MONDAY_DATE, "11:00"), at(MONDAY_DATE, "11:30"))
    before = scenario.schedule(scenario.professional_id, at(MONDAY_DATE, "09:00"), at(MONDAY_DATE, "10:00"))
    other = scenario.schedule(other_professional_id, at(MONDAY_DATE, "10:00"), at(MONDAY_DATE, "11:00"))

    expect_status(after, 201, "esperava aceitar consulta que começa às 11:00, quando a anterior termina")
    expect_status(before, 201, "esperava aceitar consulta que termina às 10:00, quando a próxima começa")
    expect_status(other, 201, "esperava aceitar consulta no mesmo horário com outro profissional")
