"""Cliente HTTP dos testes, sobre o `TestClient` do FastAPI."""

import json
import re
from typing import Any

import httpx2 as httpx
from starlette.testclient import TestClient

from tests.support.users import RECEPTIONIST, TestUser, basic_authorization

_RECEPTIONIST_AUTHORIZATION = basic_authorization(RECEPTIONIST.username, RECEPTIONIST.password)


class ApiResponse:
    def __init__(self, request: str, response: httpx.Response) -> None:
        self.request = request
        self.status = response.status_code
        self.headers = response.headers
        self.text = response.text
        try:
            self.body: Any = json.loads(self.text)
        except ValueError:
            self.body = None

    def header(self, name: str) -> str | None:
        return self.headers.get(name)

    @property
    def content_type(self) -> str:
        return self.header("content-type") or ""

    def json(self, path: str) -> Any:
        """Lê um valor do corpo JSON por um caminho como `id`, `page.totalElements` ou `content[0].start`. Devolve
        `None` quando o caminho não existe ou o corpo não é JSON, para o teste falhar na asserção seguinte."""
        value = self.body
        for part in (part for part in re.split(r"\.|\[(\d+)\]", path) if part):
            if isinstance(value, dict):
                value = value.get(part)
            elif isinstance(value, list) and part.isdigit() and int(part) < len(value):
                value = value[int(part)]
            else:
                return None
        return value

    def describe(self) -> str:
        text = " ".join(self.text.split())
        if len(text) > 500:
            text = text[:500] + "..."
        return f"{self.request} respondeu {self.status} com corpo: {text}"


class Api:
    """Por padrão, toda chamada envia as credenciais da recepcionista."""

    def __init__(self, client: TestClient, authorization: str | None = _RECEPTIONIST_AUTHORIZATION) -> None:
        self._client = client
        self._authorization = authorization

    def as_user(self, user: TestUser) -> "Api":
        return Api(self._client, basic_authorization(user.username, user.password))

    def with_credentials(self, username: str, password: str) -> "Api":
        return Api(self._client, basic_authorization(username, password))

    def anonymous(self) -> "Api":
        return Api(self._client, None)

    def get(self, path: str) -> ApiResponse:
        return self._perform("GET", path)

    def post(self, path: str, body: dict[str, Any] | str | None = None) -> ApiResponse:
        return self._perform("POST", path, body)

    def put(self, path: str, body: dict[str, Any] | str | None = None) -> ApiResponse:
        return self._perform("PUT", path, body)

    def delete(self, path: str) -> ApiResponse:
        return self._perform("DELETE", path)

    def _perform(self, method: str, path: str, body: dict[str, Any] | str | None = None) -> ApiResponse:
        headers = {"Accept": "application/json, application/problem+json"}
        if self._authorization is not None:
            headers["Authorization"] = self._authorization
        content = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            content = body if isinstance(body, str) else json.dumps(body)
        response = self._client.request(method, path, headers=headers, content=content)
        return ApiResponse(f"{method} {path}", response)


def expect_status(response: ApiResponse, status: int, message: str) -> None:
    """Confere o status HTTP, com a resposta completa na mensagem de falha."""
    assert response.status == status, f"{message}; {response.describe()}"
