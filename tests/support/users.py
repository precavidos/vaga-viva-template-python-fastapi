"""Usuários de teste. Os mesmos dados estão em `tests/config/security-users.json`, o arquivo indicado pela variável
`CLINIC_SECURITY_USERS_FILE` durante os testes."""

import base64
from dataclasses import dataclass

SECURITY_USERS_FILE = "tests/config/security-users.json"


@dataclass(frozen=True)
class TestUser:
    __test__ = False

    username: str
    password: str


RECEPTIONIST = TestUser("recepcao", "recepcao-senha")
PROFESSIONAL = TestUser("dra.helena", "profissional-senha")


def basic_authorization(username: str, password: str) -> str:
    return "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode("ascii")
