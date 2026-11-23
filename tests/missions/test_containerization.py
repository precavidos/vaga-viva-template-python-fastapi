import json
from typing import Any

import httpx2
import pytest
import yaml
from testcontainers.community.postgres import PostgresContainer
from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage
from testcontainers.core.network import Network
from testcontainers.core.wait_strategies import HttpWaitStrategy

from tests.conftest import POSTGRES_IMAGE
from tests.support.missions import PROJECT_ROOT

pytestmark = pytest.mark.mission("containerization")

COMPOSE = "compose.yaml"
POSTGRES_17 = ("postgres:17", "library/postgres:17", "docker.io/library/postgres:17", "docker.io/postgres:17")


def services() -> dict[str, Any]:
    file = PROJECT_ROOT / "compose.yaml"
    assert file.is_file(), f"esperava encontrar o arquivo {COMPOSE} na raiz do projeto"
    try:
        compose = yaml.safe_load(file.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        pytest.fail(f"esperava que {COMPOSE} fosse um YAML válido: {error}", pytrace=False)
    found = compose.get("services") if isinstance(compose, dict) else None
    assert isinstance(found, dict), f"esperava a chave 'services' em {COMPOSE}"
    return found


def app_service(found: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    return next(
        ((name, service) for name, service in found.items() if isinstance(service, dict) and "build" in service), None
    )


def database_service(found: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    return next(
        (
            (name, service)
            for name, service in found.items()
            if isinstance(service, dict) and str(service.get("image", "")).startswith(POSTGRES_17)
        ),
        None,
    )


def environment(service: dict[str, Any]) -> dict[str, str]:
    value = service.get("environment")
    if isinstance(value, list):
        return dict(str(item).partition("=")[::2] for item in value)
    if isinstance(value, dict):
        return {str(key): str(item) for key, item in value.items()}
    return {}


@pytest.mark.timeout(600)
def test_a_imagem_do_dockerfile_sobe_e_responde_em_health_conectada_ao_postgresql():
    assert (PROJECT_ROOT / "Dockerfile").is_file(), "esperava encontrar o arquivo Dockerfile na raiz do projeto"

    failure: str | None = None
    body = ""
    try:
        with Network() as network:
            database = (
                PostgresContainer(POSTGRES_IMAGE, username="clinic", password="clinic", dbname="clinic", driver=None)
                .with_network(network)
                .with_network_aliases("db")
            )
            with database, DockerImage(path=PROJECT_ROOT, tag="vaga-viva-clinic-test", clean_up=False) as image:
                app = (
                    DockerContainer(str(image))
                    .with_network(network)
                    .with_env("DATABASE_URL", "postgresql://clinic:clinic@db:5432/clinic")
                    .with_exposed_ports(8080)
                    .waiting_for(HttpWaitStrategy(8080, "/health").for_status_code(200).with_startup_timeout(180))
                )
                with app:
                    url = f"http://{app.get_container_host_ip()}:{app.get_exposed_port(8080)}/health"
                    body = httpx2.get(url, timeout=10).text
    except Exception as error:
        failure = f"{type(error).__name__}: {error}"

    assert failure is None, (
        "esperava construir a imagem do Dockerfile e ver a aplicação responder 200 em /health na porta 8080, "
        f"usando a variável DATABASE_URL; erro: {failure}"
    )
    assert '"ok"' in body, f'esperava {{"status":"ok"}} em /health dentro do contêiner; recebeu {body!r}'


def test_o_compose_yaml_declara_a_aplicacao_construida_do_dockerfile_e_o_postgresql_17():
    found = services()

    assert app_service(found) is not None, f"esperava em {COMPOSE} um serviço com 'build' para a aplicação"
    assert database_service(found) is not None, (
        f"esperava em {COMPOSE} um serviço com 'image: postgres:17' (ou uma variante, como postgres:17-alpine)"
    )


def test_o_compose_yaml_publica_a_porta_8080_e_liga_a_aplicacao_ao_banco_pelo_nome_do_servico():
    found = services()
    app = (app_service(found) or ("", {}))[1]
    database_name = (database_service(found) or ("?", {}))[0]
    ports = [json.dumps(port) for port in app.get("ports", [])] if isinstance(app.get("ports"), list) else []

    assert any("8080" in port for port in ports), "esperava a porta 8080 da aplicação em 'ports'"
    assert f"@{database_name}:" in environment(app).get("DATABASE_URL", ""), (
        f"esperava DATABASE_URL apontando para o serviço do banco ('{database_name}'), "
        f"como postgresql://clinic:clinic@{database_name}:5432/clinic"
    )
