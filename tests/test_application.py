from tests.support.dates import MONDAY, at, future_date


def test_health_responde_200_sem_credenciais(api):
    response = api.anonymous().get("/health")

    assert response.status == 200, response.describe()
    assert response.body == {"status": "ok"}, response.describe()


def test_migracao_inicial_cria_professionals_e_appointments(db):
    assert {"id", "name", "specialty"} <= set(db.columns("professionals"))
    assert {"id", "professional_id", "patient_id", "starts_at", "duration_minutes"} <= set(db.columns("appointments"))


def test_consulta_aceita_qualquer_patient_id_sem_chave_estrangeira(db):
    professional_id = db.insert_professional()

    db.insert_appointment(professional_id, 999, at(future_date(MONDAY), "10:00"), 30)

    assert db.count_appointments() == 1
