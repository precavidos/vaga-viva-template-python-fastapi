from typing import Any

import pytest

from tests.support.api import Api, ApiResponse, expect_status
from tests.support.database import Database
from tests.support.dates import MONDAY, THURSDAY, TUESDAY, WEDNESDAY, at, future_date, local_date_time, plus_minutes

pytestmark = pytest.mark.mission("pagination")

PATIENT_ID = 1
MON09 = at(future_date(MONDAY), "09:00")
MON14 = at(future_date(MONDAY), "14:00")
TUE10 = at(future_date(TUESDAY), "10:00")
WED08 = at(future_date(WEDNESDAY), "08:00")
THU16 = at(future_date(THURSDAY), "16:00")


@pytest.fixture
def professional_id(db: Database) -> int:
    professional = db.insert_professional()
    other_professional = db.insert_professional("Dr. Rafael Moura", "Cardiologia")
    db.insert_appointment(professional, PATIENT_ID, TUE10, 30)
    db.insert_appointment(professional, PATIENT_ID, THU16, 60)
    db.insert_appointment(professional, PATIENT_ID, MON14, 30)
    db.insert_appointment(professional, PATIENT_ID, WED08, 45)
    db.insert_appointment(professional, PATIENT_ID, MON09, 30)
    db.insert_appointment(other_professional, PATIENT_ID, MON09, 30)
    db.insert_appointment(other_professional, PATIENT_ID, TUE10, 30)
    return professional


def list_appointments(api: Api, query: str, professional: int) -> ApiResponse:
    response = api.get(f"/professionals/{professional}/appointments{query}")
    expect_status(response, 200, "esperava status 200 em GET /professionals/{id}/appointments")
    return response


def content(response: ApiResponse) -> list[dict[str, Any]]:
    items = response.json("content")
    assert isinstance(items, list), f"esperava a lista 'content' na resposta; {response.describe()}"
    return items


def starts(response: ApiResponse) -> list[object]:
    return [local_date_time(item.get("start")) for item in content(response)]


def expect_page(response: ApiResponse, number: int, size: int, total_elements: int, total_pages: int) -> None:
    assert response.json("page.number") == number, f"esperava page.number = {number}; {response.describe()}"
    assert response.json("page.size") == size, f"esperava page.size = {size}; {response.describe()}"
    assert response.json("page.totalElements") == total_elements, (
        f"esperava page.totalElements = {total_elements}; {response.describe()}"
    )
    assert response.json("page.totalPages") == total_pages, (
        f"esperava page.totalPages = {total_pages}; {response.describe()}"
    )


def test_devolve_a_primeira_pagina_ordenada_pela_data_de_inicio(api, professional_id):
    response = list_appointments(api, "?page=0&size=2", professional_id)

    assert starts(response) == [MON09, MON14], "esperava as 2 primeiras consultas, em ordem crescente de início"
    expect_page(response, 0, 2, 5, 3)


def test_devolve_a_ultima_pagina_com_os_dados_de_cada_consulta(api, professional_id):
    response = list_appointments(api, "?page=2&size=2", professional_id)

    assert starts(response) == [THU16], "esperava só a última consulta na página 2"
    assert isinstance(response.json("content[0].id"), int), "esperava o campo 'id' em cada consulta"
    assert response.json("content[0].professionalId") == professional_id, (
        "esperava o campo 'professionalId' em cada consulta"
    )
    assert response.json("content[0].patientId") == PATIENT_ID, "esperava o campo 'patientId' em cada consulta"
    assert local_date_time(response.json("content[0].end")) == plus_minutes(THU16, 60), (
        "esperava o campo 'end' = início + duração em cada consulta"
    )
    assert response.json("content[0].durationMinutes") == 60, "esperava o campo 'durationMinutes' em cada consulta"
    expect_page(response, 2, 2, 5, 3)


def test_lista_so_as_consultas_do_profissional_com_20_itens_por_pagina_por_padrao(api, professional_id):
    response = list_appointments(api, "", professional_id)

    assert starts(response) == [MON09, MON14, TUE10, WED08, THU16], (
        "esperava as 5 consultas do profissional, sem as de outro profissional"
    )
    assert [item.get("professionalId") for item in content(response)] == [professional_id] * 5, (
        "esperava só consultas do profissional pedido"
    )
    expect_page(response, 0, 20, 5, 1)


def test_ordena_da_mais_recente_para_a_mais_antiga_com_sort_start_desc(api, professional_id):
    response = list_appointments(api, "?page=0&size=3&sort=start,desc", professional_id)

    assert starts(response) == [THU16, WED08, TUE10], "esperava as consultas em ordem decrescente de início"
    expect_page(response, 0, 3, 5, 2)


def test_devolve_uma_pagina_vazia_para_um_profissional_sem_consultas(api, db, professional_id):
    without_appointments = db.insert_professional("Dra. Beatriz Lins", "Pediatria")

    response = list_appointments(api, "?page=0&size=10", without_appointments)

    assert content(response) == [], "esperava a lista 'content' vazia"
    expect_page(response, 0, 10, 0, 0)
