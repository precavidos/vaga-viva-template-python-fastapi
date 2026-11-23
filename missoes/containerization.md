# Missão `containerization`: aplicação em contêiner

Empacote a aplicação em uma imagem Docker e suba tudo com Docker Compose.

Testes: `tests/missions/test_containerization.py`. Para rodar só esta missão: `uv run pytest --mission containerization`. O primeiro teste constrói a imagem e pode levar alguns minutos (o limite é de 10 minutos).

## `Dockerfile`, na raiz do projeto

- O contexto do build é a raiz do projeto. A imagem precisa ser construída só a partir do código-fonte: a instalação das dependências acontece dentro do `docker build`.
- Use só fontes públicas: uma imagem oficial do Python 3.13 do Docker Hub (por exemplo, `python:3.13-slim`) e os pacotes do PyPI. O `uv` também está no PyPI (`pip install uv`), e `uv sync --locked --no-dev` instala as versões do `uv.lock`.
- A aplicação escuta na porta `8080` e responde `200` com `{"status":"ok"}` em `/health`.
- A conexão com o banco vem da variável de ambiente `DATABASE_URL`. O teste usa `postgresql://clinic:clinic@db:5432/clinic`, com o banco vazio: a aplicação aplica as migrações do Alembic ao subir (`alembic upgrade heads`).
- Sugestão: instale as dependências numa camada separada do código-fonte (copie `pyproject.toml` e `uv.lock` antes, e `app/`, `migrations/` e `alembic.ini` depois), assim o Docker reaproveita o cache das dependências quando só o código muda. Um `.dockerignore` que exclua `.venv/`, `reports/` e `__pycache__/` também deixa o build mais rápido.

## `compose.yaml`, na raiz do projeto

- Um serviço para a aplicação, com `build` apontando para o `Dockerfile` e a porta `8080` publicada em `ports`.
- Um serviço para o banco com a imagem `postgres:17` (ou uma variante, como `postgres:17-alpine`).
- No serviço da aplicação, `environment` define `DATABASE_URL` apontando para o serviço do banco pelo nome dele (por exemplo, `postgresql://clinic:clinic@db:5432/clinic`).
