import pytest

from tests.support.api import expect_status
from tests.support.patients import create_patient, new_patient

pytestmark = pytest.mark.mission("patients-api")


def test_cadastra_um_paciente_e_devolve_201_o_cabecalho_location_e_os_dados_com_o_id(api):
    patient = new_patient()

    response = api.post("/patients", patient)

    expect_status(response, 201, "esperava status 201 em POST /patients")
    patient_id = response.json("id")
    assert isinstance(patient_id, int), f"esperava o campo 'id' numérico na resposta; {response.describe()}"
    assert (response.header("Location") or "").endswith(f"/patients/{patient_id}"), (
        f"esperava o cabeçalho Location apontando para /patients/{{id}}; recebeu {response.header('Location')!r}"
    )
    assert response.json("name") == patient["name"], "esperava o campo 'name' na resposta"
    assert response.json("email") == patient["email"], "esperava o campo 'email' na resposta"
    assert response.json("phone") == patient["phone"], "esperava o campo 'phone' na resposta"
    assert response.json("birthDate") == patient["birthDate"], "esperava o campo 'birthDate' (AAAA-MM-DD) na resposta"


def test_busca_um_paciente_cadastrado_pelo_id(api):
    patient = new_patient()
    patient_id = create_patient(api, patient)

    response = api.get(f"/patients/{patient_id}")

    expect_status(response, 200, f"esperava status 200 em GET /patients/{patient_id}")
    assert response.json("id") == patient_id, "esperava o mesmo id na resposta"
    assert response.json("name") == patient["name"], "esperava o nome cadastrado"
    assert response.json("email") == patient["email"], "esperava o e-mail cadastrado"


def test_altera_os_dados_de_um_paciente(api):
    patient_id = create_patient(api)
    changed = {
        "name": "Paciente Alterado",
        "email": f"alterado{patient_id}@example.com",
        "phone": "+55 21 98888-0000",
        "birthDate": "1985-01-30",
    }

    update = api.put(f"/patients/{patient_id}", changed)

    expect_status(update, 200, f"esperava status 200 em PUT /patients/{patient_id}")
    assert update.json("name") == changed["name"], "esperava o nome novo na resposta do PUT"
    found = api.get(f"/patients/{patient_id}")
    assert found.json("name") == changed["name"], f"esperava o nome novo ao buscar o paciente; {found.describe()}"
    assert found.json("email") == changed["email"], "esperava o e-mail novo ao buscar o paciente"
    assert found.json("phone") == changed["phone"], "esperava o telefone novo ao buscar o paciente"
    assert found.json("birthDate") == changed["birthDate"], "esperava a data de nascimento nova ao buscar o paciente"


def test_remove_um_paciente_que_deixa_de_ser_encontrado(api):
    patient_id = create_patient(api)

    deleted = api.delete(f"/patients/{patient_id}")

    expect_status(deleted, 204, f"esperava status 204 em DELETE /patients/{patient_id}")
    found = api.get(f"/patients/{patient_id}")
    expect_status(found, 404, "esperava status 404 ao buscar um paciente removido")


def test_responde_404_ao_alterar_ou_remover_um_paciente_que_nao_existe(api):
    patient_id = create_patient(api)
    api.delete(f"/patients/{patient_id}")

    update = api.put(f"/patients/{patient_id}", new_patient())
    deleted = api.delete(f"/patients/{patient_id}")

    expect_status(update, 404, "esperava status 404 ao alterar um paciente removido")
    expect_status(deleted, 404, "esperava status 404 ao remover de novo um paciente")
