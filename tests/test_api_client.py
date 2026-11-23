from collections.abc import Iterator

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from tests.support.api import Api
from tests.support.users import PROFESSIONAL, basic_authorization


@pytest.fixture
def echo() -> Iterator[Api]:
    app = FastAPI()

    @app.api_route("/echo", methods=["GET", "POST"])
    async def handler(request: Request) -> dict[str, object]:
        return {"authorization": request.headers.get("authorization"), "body": (await request.body()).decode()}

    with TestClient(app) as client:
        yield Api(client)


def test_envia_as_credenciais_da_recepcionista_por_padrao(echo):
    assert echo.get("/echo").json("authorization") == basic_authorization("recepcao", "recepcao-senha")


def test_anonymous_nao_envia_credenciais(echo):
    assert echo.anonymous().get("/echo").json("authorization") is None


def test_as_user_envia_as_credenciais_do_usuario(echo):
    assert echo.as_user(PROFESSIONAL).get("/echo").json("authorization") == basic_authorization(
        PROFESSIONAL.username, PROFESSIONAL.password
    )


def test_le_caminhos_do_corpo_json_e_envia_texto_cru(echo):
    response = echo.post("/echo", '{"name": ')

    assert response.json("body") == '{"name": '
    assert response.json("nada.aqui[0]") is None
