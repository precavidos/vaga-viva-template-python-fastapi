import re
from datetime import date, timedelta

import pytest

from tests.support.api import ApiResponse, expect_status
from tests.support.patients import create_patient, new_patient

pytestmark = pytest.mark.mission("input-validation")

ENGLISH_DEFAULT_MESSAGE = re.compile(
    r"\b(should|must|Bad Request|Unexpected|Expected|Expecting|is not|invalid|required|failed"
    r"|Field|Input|decode|error)\b",
    re.IGNORECASE,
)
"""Trechos das mensagens padrão, em inglês, do FastAPI, do Pydantic e do parser de JSON."""


def expect_portuguese(message: object, description: str) -> None:
    assert isinstance(message, str) and message.strip(), description
    assert not ENGLISH_DEFAULT_MESSAGE.search(message), f"{description}; recebeu {message!r}"


def expect_problem(response: ApiResponse) -> None:
    expect_status(response, 400, "esperava status 400 para dados inválidos")
    assert response.content_type.startswith("application/problem+json"), (
        f"esperava Content-Type application/problem+json (Problem Details, RFC 9457); {response.describe()}"
    )
    assert response.json("status") == 400, "esperava o campo 'status' igual a 400 no corpo do erro"
    assert isinstance(response.json("title"), str), "esperava o campo 'title' no corpo do erro"
    expect_portuguese(
        response.json("detail"), f"esperava o campo 'detail', em português, no corpo do erro; {response.describe()}"
    )


def expect_validation_problem(response: ApiResponse, *fields: str) -> None:
    expect_problem(response)
    errors = response.json("errors")
    assert isinstance(errors, list) and errors and all(isinstance(error, dict) for error in errors), (
        f"esperava a lista 'errors' com um item {{field, message}} por campo inválido; {response.describe()}"
    )
    reported = {error.get("field") for error in errors}
    assert set(fields) <= reported, f"esperava erros para os campos {', '.join(fields)}; {response.describe()}"
    for error in errors:
        expect_portuguese(
            error.get("message"), f"esperava uma mensagem clara, em português, para o campo {error.get('field')}"
        )


def test_recusa_paciente_sem_nome_com_400_e_problem_details_apontando_o_campo(api):
    response = api.post("/patients", {**new_patient(), "name": " "})

    expect_validation_problem(response, "name")


def test_recusa_email_invalido(api):
    response = api.post("/patients", {**new_patient(), "email": "nao-e-um-email"})

    expect_validation_problem(response, "email")


def test_recusa_data_de_nascimento_no_futuro(api):
    next_year = (date.today() + timedelta(days=366)).isoformat()

    response = api.post("/patients", {**new_patient(), "birthDate": next_year})

    expect_validation_problem(response, "birthDate")


def test_aponta_todos_os_campos_obrigatorios_que_faltam_de_uma_vez(api):
    response = api.post("/patients", {})

    expect_validation_problem(response, "name", "email", "phone", "birthDate")


def test_valida_tambem_a_alteracao_de_um_paciente(api):
    patient_id = create_patient(api)

    response = api.put(f"/patients/{patient_id}", {**new_patient(), "name": ""})

    expect_validation_problem(response, "name")


def test_recusa_json_malformado_com_400_e_problem_details(api):
    response = api.post("/patients", '{"name": ')

    expect_problem(response)
