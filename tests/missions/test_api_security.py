import pytest

from tests.support.api import expect_status
from tests.support.dates import MONDAY, at, future_date
from tests.support.patients import create_patient, new_patient
from tests.support.users import PROFESSIONAL, RECEPTIONIST

pytestmark = pytest.mark.mission("api-security")


def test_sem_credenciais_recusa_a_api_com_401_e_mantem_health_publico(api):
    anonymous = api.anonymous()

    get = anonymous.get("/patients/1")
    post = anonymous.post("/patients", new_patient())
    health = anonymous.get("/health")

    expect_status(get, 401, "esperava 401 em GET /patients/1 sem credenciais")
    expect_status(post, 401, "esperava 401 em POST /patients sem credenciais")
    expect_status(health, 200, "esperava /health público (200) sem credenciais")


def test_recusa_com_401_senha_errada_e_usuario_desconhecido(api):
    wrong_password = api.with_credentials(RECEPTIONIST.username, "senha-errada").get("/patients/1")
    unknown_user = api.with_credentials("ninguem", "qualquer").get("/patients/1")

    expect_status(wrong_password, 401, "esperava 401 com senha errada")
    expect_status(unknown_user, 401, "esperava 401 com usuário desconhecido")


def test_o_profissional_consulta_pacientes_mas_nao_cadastra_altera_nem_remove(api):
    patient_id = create_patient(api)
    professional = api.as_user(PROFESSIONAL)

    get = professional.get(f"/patients/{patient_id}")
    post = professional.post("/patients", new_patient())
    put = professional.put(f"/patients/{patient_id}", new_patient())
    deleted = professional.delete(f"/patients/{patient_id}")

    expect_status(get, 200, "esperava 200 quando o profissional consulta um paciente")
    expect_status(post, 403, "esperava 403 quando o profissional tenta cadastrar paciente")
    expect_status(put, 403, "esperava 403 quando o profissional tenta alterar paciente")
    expect_status(deleted, 403, "esperava 403 quando o profissional tenta remover paciente")
    assert get.header("Set-Cookie") is None, "esperava uma API sem sessão: nenhum cookie na resposta"


def test_a_recepcionista_agenda_consultas_o_profissional_nao(api, db):
    patient_id = create_patient(api)
    professional_id = db.insert_professional()
    monday = future_date(MONDAY)

    denied = api.as_user(PROFESSIONAL).post(
        "/appointments",
        {
            "patientId": patient_id,
            "professionalId": professional_id,
            "start": at(monday, "10:00"),
            "end": at(monday, "10:30"),
        },
    )
    allowed = api.as_user(RECEPTIONIST).post(
        "/appointments",
        {
            "patientId": patient_id,
            "professionalId": professional_id,
            "start": at(monday, "11:00"),
            "end": at(monday, "11:30"),
        },
    )

    expect_status(denied, 403, "esperava 403 quando o profissional tenta agendar")
    expect_status(allowed, 201, "esperava 201 quando a recepcionista agenda")
