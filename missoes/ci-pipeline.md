# Missão `ci-pipeline`: pipeline de integração contínua

Rode a instalação e os testes a cada push com GitHub Actions.

Testes: `tests/missions/test_ci_pipeline.py`. Para rodar só esta missão: `uv run pytest --mission ci-pipeline`.

## Contrato

Crie o arquivo `.github/workflows/ci.yml`. Os testes leem esse YAML e conferem que:

- ele dispara nos eventos `push` e `pull_request`;
- um passo usa `astral-sh/setup-uv` com `python-version: "3.13"`;
- um passo roda `uv sync` e um passo roda `uv run pytest`.

O arquivo `.github/workflows/vaga-viva.yml` é do Vaga Viva e não faz parte da missão. Não o altere nem o use como resposta.
