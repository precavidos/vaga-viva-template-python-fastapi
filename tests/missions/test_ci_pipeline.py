import re
from typing import Any

import pytest
import yaml

from tests.support.missions import PROJECT_ROOT

pytestmark = pytest.mark.mission("ci-pipeline")

WORKFLOW = ".github/workflows/ci.yml"


def load_workflow() -> dict[Any, Any]:
    file = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
    assert file.is_file(), f"esperava encontrar o arquivo {WORKFLOW} na raiz do projeto"
    try:
        workflow = yaml.safe_load(file.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        pytest.fail(f"esperava que {WORKFLOW} fosse um YAML válido: {error}", pytrace=False)
    assert isinstance(workflow, dict), f"esperava que {WORKFLOW} fosse um YAML com as chaves 'on' e 'jobs'"
    return workflow


def events(workflow: dict[Any, Any]) -> list[str]:
    # O YAML 1.1 lê a chave `on` sem aspas como o booleano True.
    on = workflow.get("on", workflow.get(True))
    if isinstance(on, str):
        return [on]
    if isinstance(on, list):
        return [str(event) for event in on]
    if isinstance(on, dict):
        return [str(event) for event in on]
    return []


def steps(workflow: dict[Any, Any]) -> list[dict[str, Any]]:
    jobs = workflow.get("jobs")
    found: list[dict[str, Any]] = []
    if isinstance(jobs, dict):
        for job in jobs.values():
            job_steps = job.get("steps") if isinstance(job, dict) else None
            if isinstance(job_steps, list):
                found.extend(step for step in job_steps if isinstance(step, dict))
    assert found, f"esperava ao menos um job com 'steps' em {WORKFLOW}"
    return found


def test_o_workflow_ci_yml_dispara_a_cada_push_e_a_cada_pull_request():
    workflow = load_workflow()

    assert {"push", "pull_request"} <= set(events(workflow)), (
        f"esperava os eventos push e pull_request na chave 'on' de {WORKFLOW}"
    )


def test_o_workflow_usa_o_uv_com_python_3_13():
    all_steps = steps(load_workflow())
    setup_uv = [step for step in all_steps if str(step.get("uses", "")).startswith("astral-sh/setup-uv")]

    assert setup_uv, f"esperava um passo com 'uses: astral-sh/setup-uv' em {WORKFLOW}"
    python_versions = [
        str((step.get("with") or {}).get("python-version", ""))
        for step in all_steps
        if str(step.get("uses", "")).startswith(("astral-sh/setup-uv", "actions/setup-python"))
    ]
    commands = [step["run"] for step in all_steps if isinstance(step.get("run"), str)]
    assert any(version.startswith("3.13") for version in python_versions) or any(
        re.search(r"\buv python install 3\.13\b", command) for command in commands
    ), "esperava o Python 3.13 configurado no workflow (python-version: 3.13 no astral-sh/setup-uv)"


def test_o_workflow_roda_uv_sync_e_uv_run_pytest():
    commands = [step["run"] for step in steps(load_workflow()) if isinstance(step.get("run"), str)]

    assert any(re.search(r"\buv sync\b", command) for command in commands), (
        f"esperava um passo 'run' que execute uv sync em {WORKFLOW}"
    )
    assert any(re.search(r"\buv run pytest\b", command) for command in commands), (
        f"esperava um passo 'run' que execute uv run pytest em {WORKFLOW}"
    )
