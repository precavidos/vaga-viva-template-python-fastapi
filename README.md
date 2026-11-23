# Vaga Viva: modelo Python/FastAPI

Repositório-modelo do arquétipo `python-fastapi` do Vaga Viva: a API de um sistema fictício de agendamento de clínica, com pacientes, profissionais e consultas.

O projeto começa incompleto. Cada missão do seu plano tem testes automatizados que falham até você implementá-la. O contrato de cada missão está em `missoes/`.

## Tecnologias

Python 3.13, FastAPI, Pydantic v2, pydantic-settings, SQLAlchemy 2, psycopg 3, Alembic, PostgreSQL 17, pytest e Testcontainers. As dependências são gerenciadas pelo [uv](https://docs.astral.sh/uv/).

## Pré-requisitos

- [uv](https://docs.astral.sh/uv/getting-started/installation/). Ele instala o Python 3.13 sozinho, se for preciso.
- Docker em execução: os testes sobem um PostgreSQL com Testcontainers.

## Comandos

| Para | Rode |
| --- | --- |
| instalar as dependências | `uv sync` |
| rodar todos os testes | `uv run pytest` |
| rodar os testes de uma missão | `uv run pytest --mission <id-da-missão>`, por exemplo `uv run pytest --mission patients-api` |
| aplicar as migrações | `uv run alembic upgrade heads`, com um PostgreSQL em `DATABASE_URL` |
| criar uma migração | `uv run alembic revision -m "descrição"` (ou com `--autogenerate`, a partir dos modelos) |
| subir a aplicação | `uv run uvicorn app.main:app --port 8080` |

Para subir um PostgreSQL local:

```sh
docker run --rm -p 5432:5432 -e POSTGRES_DB=clinic -e POSTGRES_USER=clinic -e POSTGRES_PASSWORD=clinic postgres:17-alpine
```

A aplicação responde `{"status":"ok"}` em `http://localhost:8080/health`.

## Configuração

Tudo vem de variáveis de ambiente, lidas pelo pydantic-settings em `app/config.py` (`get_settings()`). Os valores padrão estão abaixo.

| Variável | Padrão |
| --- | --- |
| `DATABASE_URL` | `postgresql://clinic:clinic@localhost:5432/clinic` |
| `CLINIC_TIME_ZONE` | `America/Sao_Paulo` |
| `CLINIC_OPENING_DAYS` | `MONDAY,TUESDAY,WEDNESDAY,THURSDAY,FRIDAY` |
| `CLINIC_OPENS_AT` | `08:00` |
| `CLINIC_CLOSES_AT` | `18:00` |

Nos testes, `DATABASE_URL` aponta para o PostgreSQL do Testcontainers, e `CLINIC_SECURITY_USERS_FILE` aponta para `tests/config/security-users.json` (veja a missão `api-security`).

## Seu plano: `.vaga-viva/plan.json`

O Vaga Viva cria o arquivo `.vaga-viva/plan.json` no seu repositório com as missões que você escolheu:

```json
{
  "archetype": "python-fastapi",
  "domain": "clinic-scheduling",
  "missions": ["patients-api", "persistence", "scheduling-rules", "pagination", "availability-query", "containerization"]
}
```

Os testes das missões fora do plano aparecem como ignorados (*skipped*), com o motivo, e não como falhas. Sem esse arquivo, os testes de todas as missões rodam. Os testes que não pertencem a nenhuma missão sempre rodam.

O workflow `.github/workflows/vaga-viva.yml` roda `uv sync --locked` e `uv run pytest` a cada push na `main` e a cada pull request, e guarda o relatório dos testes (`reports/junit.xml`). Ele é do Vaga Viva: não o altere.

## Missões

| Missão | Contrato |
| --- | --- |
| `patients-api` | [Cadastro de pacientes](missoes/patients-api.md) |
| `persistence` | [Pacientes no banco de dados](missoes/persistence.md) |
| `scheduling-rules` | [Regras de agendamento](missoes/scheduling-rules.md) |
| `input-validation` | [Validação e mensagens de erro](missoes/input-validation.md) |
| `bug-hunt` | [Caça ao bug](missoes/bug-hunt.md) |
| `pagination` | [Listagem paginada de consultas](missoes/pagination.md) |
| `ci-pipeline` | [Pipeline de integração contínua](missoes/ci-pipeline.md) |
| `availability-query` | [Consulta de horários livres](missoes/availability-query.md) |
| `containerization` | [Aplicação em contêiner](missoes/containerization.md) |
| `reminder-strategies` | [Lembretes por e-mail e SMS](missoes/reminder-strategies.md) |
| `api-security` | [Proteção da API](missoes/api-security.md) |

Os testes de cada missão ficam em `tests/missions/test_<id>.py`, com `-` trocado por `_` (por exemplo, `tests/missions/test_patients_api.py`). Leia os testes e as mensagens de falha: elas dizem o que ainda falta.

## Estrutura

```
app/
  main.py           create_app(): monta a aplicação, usada também pelos testes
  config.py         configuração lida das variáveis de ambiente (get_settings)
  clock.py          relógio no fuso da clínica (get_clock)
  database.py       engine e sessão do SQLAlchemy (get_session) e a base dos modelos
  models.py         modelos Professional e Appointment
  errors.py         tratadores de erro da aplicação
  health.py         GET /health
  appointments/     cálculo da duração das consultas
  professionals/    rotas dos profissionais
  reminders/        contratos de envio de lembretes
migrations/
  versions/         migrações do Alembic
tests/
  missions/         testes das missões
  support/          infraestrutura dos testes (PostgreSQL, cliente HTTP, dados fictícios, plano)
  config/           usuários de teste
conftest.py         leitura do plano e opção --mission
```

Todos os dados do projeto são fictícios.

## Licença

[MIT](LICENSE).
