import pytest

from app.database import Base
from tests.support.api import expect_status
from tests.support.database import Database
from tests.support.patients import create_patient, new_patient

pytestmark = pytest.mark.mission("persistence")

INITIAL_MIGRATION = "0001_initial"


def expect_patients_table(db: Database) -> None:
    assert db.table_exists("patients"), (
        "esperava a tabela patients no PostgreSQL, criada por uma migração nova do Alembic em migrations/versions"
    )


def test_cria_a_tabela_patients_com_uma_migracao_do_alembic_a_partir_de_um_modelo_patient(db, app):
    expect_patients_table(db)
    assert {"id", "name", "email", "phone", "birth_date"} <= set(db.columns("patients")), (
        "esperava as colunas id, name, email, phone e birth_date na tabela patients; "
        f"encontrou {db.columns('patients')}"
    )
    versions = [row["version_num"] for row in db.query("SELECT version_num FROM alembic_version")]
    assert any(version != INITIAL_MIGRATION for version in versions), (
        f"esperava uma migração nova do Alembic em migrations/versions, além da {INITIAL_MIGRATION}"
    )
    mapped = [mapper.class_.__name__ for mapper in Base.registry.mappers if mapper.local_table.name == "patients"]
    assert mapped == ["Patient"], (
        "esperava um modelo Patient do SQLAlchemy, herdando de app.database.Base, ligado à tabela patients"
    )


def test_grava_na_tabela_patients_o_paciente_cadastrado_pela_api(db, api):
    expect_patients_table(db)
    patient = new_patient()

    patient_id = create_patient(api, patient)

    rows = db.query(
        "SELECT name, email, phone, birth_date::text AS birth_date FROM patients WHERE id = %s", (patient_id,)
    )
    assert len(rows) == 1, f"esperava encontrar na tabela patients a linha com id {patient_id}"
    assert rows[0] == {
        "name": patient["name"],
        "email": patient["email"],
        "phone": patient["phone"],
        "birth_date": patient["birthDate"],
    }, "esperava os dados do paciente nas colunas da tabela patients"


def test_le_do_banco_um_paciente_inserido_direto_na_tabela_aparece_na_api(db, api):
    expect_patients_table(db)
    [row] = db.query(
        "INSERT INTO patients (name, email, phone, birth_date) "
        "VALUES ('Paciente Do Banco', 'banco@example.com', '+55 11 90000-9999', DATE '1970-12-01') RETURNING id"
    )

    response = api.get(f"/patients/{row['id']}")

    expect_status(response, 200, "esperava status 200 ao buscar pela API um paciente gravado no banco")
    assert response.json("name") == "Paciente Do Banco", "esperava o nome que está no banco"
    assert response.json("birthDate") == "1970-12-01", "esperava a data de nascimento que está no banco"


def test_altera_e_remove_o_paciente_no_banco_quando_a_api_altera_e_remove(db, api):
    expect_patients_table(db)
    patient_id = create_patient(api)
    changed = {
        "name": "Nome Novo No Banco",
        "email": f"novo{patient_id}@example.com",
        "phone": "+55 31 97777-0000",
        "birthDate": "2001-07-07",
    }

    api.put(f"/patients/{patient_id}", changed)
    updated = db.query("SELECT name FROM patients WHERE id = %s", (patient_id,))
    api.delete(f"/patients/{patient_id}")
    remaining = db.query("SELECT count(*)::int AS count FROM patients WHERE id = %s", (patient_id,))

    assert updated and updated[0]["name"] == changed["name"], "esperava o nome alterado pela API na tabela patients"
    assert remaining[0]["count"] == 0, "esperava que o paciente removido pela API saísse da tabela patients"
