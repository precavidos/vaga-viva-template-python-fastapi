from itertools import count
from typing import Any

from tests.support.api import Api, expect_status

_sequence = count(1)


def new_patient() -> dict[str, str]:
    """Paciente fictício, com e-mail em example.com."""
    n = next(_sequence)
    return {
        "name": f"Paciente Teste {n}",
        "email": f"paciente{n}@example.com",
        "phone": f"+55 11 90000-{n % 10000:04d}",
        "birthDate": "1990-05-17",
    }


def create_patient(api: Api, patient: dict[str, Any] | None = None) -> int:
    """Cadastra um paciente pela API da missão patients-api e devolve o id."""
    response = api.post("/patients", patient if patient is not None else new_patient())
    expect_status(response, 201, "esperava status 201 ao cadastrar um paciente em POST /patients (missão patients-api)")
    patient_id = response.json("id")
    assert isinstance(patient_id, int), (
        f"esperava o campo 'id' numérico na resposta de POST /patients; {response.describe()}"
    )
    return patient_id
