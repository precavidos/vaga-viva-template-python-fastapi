# Missão `persistence`: pacientes no banco de dados

Guarde os pacientes no PostgreSQL com o SQLAlchemy e crie o esquema com uma migração do Alembic.

Testes: `tests/missions/test_persistence.py`. Para rodar só esta missão: `uv run pytest --mission persistence`.

## Contrato

- A API de pacientes (missão `patients-api`) continua igual, mas lê e grava no banco.
- Um modelo `Patient` do SQLAlchemy, que herda de `Base` (`app/database.py`) e é ligado à tabela `patients` (`__tablename__ = "patients"`).
- Tabela `patients`, criada por uma **migração nova** do Alembic em `migrations/versions`, com `down_revision = "0001_initial"` (não altere a migração `0001_initial`):

| Coluna | Conteúdo |
| --- | --- |
| `id` | identificador numérico, gerado pelo banco quando o `INSERT` não informa o valor |
| `name` | nome |
| `email` | e-mail |
| `phone` | telefone |
| `birth_date` | data de nascimento, tipo `DATE` |

- Quem cria e altera o esquema são as migrações do Alembic. Os testes aplicam as migrações com `alembic upgrade heads` antes de rodar; `Base.metadata.create_all()` não serve, porque não gera migração.
- A sessão do banco vem da dependência `get_session` (`app/database.py`), que usa `DATABASE_URL`.
- Um paciente inserido direto na tabela, por SQL, precisa aparecer em `GET /patients/{id}`. Alterar e remover pela API precisa alterar e remover a linha da tabela.

A coluna `appointments.patient_id` fica **sem** chave estrangeira para `patients`: os testes de outras missões inserem consultas com pacientes que não estão na tabela.
