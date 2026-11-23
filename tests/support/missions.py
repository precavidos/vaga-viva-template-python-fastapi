"""Missões do catálogo e leitura do plano do Vaga Viva (`.vaga-viva/plan.json`)."""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PLAN_FILE = ".vaga-viva/plan.json"
"""Caminho do plano, sempre escrito com `/` nas mensagens."""

MISSIONS: dict[str, str] = {
    "patients-api": "Cadastro de pacientes",
    "persistence": "Pacientes no banco de dados",
    "scheduling-rules": "Regras de agendamento",
    "input-validation": "Validação e mensagens de erro",
    "bug-hunt": "Caça ao bug",
    "pagination": "Listagem paginada de consultas",
    "ci-pipeline": "Pipeline de integração contínua",
    "availability-query": "Consulta de horários livres",
    "containerization": "Aplicação em contêiner",
    "reminder-strategies": "Lembretes por e-mail e SMS",
    "api-security": "Proteção da API",
}


class PlanError(Exception):
    """O arquivo de plano existe, mas não pode ser usado."""


def planned_missions(project_root: Path = PROJECT_ROOT) -> set[str] | None:
    """Missões do plano, ou `None` quando o arquivo não existe: nesse caso, todas as missões rodam."""
    file = project_root / ".vaga-viva" / "plan.json"
    if not file.exists():
        return None
    try:
        plan = json.loads(file.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise PlanError(f"Não foi possível ler {PLAN_FILE}: {error}") from error
    missions = plan.get("missions") if isinstance(plan, dict) else None
    if not isinstance(missions, list) or not all(isinstance(mission, str) for mission in missions):
        raise PlanError(f'O arquivo {PLAN_FILE} precisa ter a lista "missions" com os ids das missões')
    return set(missions)


def mission_skip_reason(mission: str, project_root: Path = PROJECT_ROOT) -> str | None:
    """Motivo para ignorar a missão, ou `None` quando ela deve rodar."""
    planned = planned_missions(project_root)
    if planned is None or mission in planned:
        return None
    return f"Missão '{mission}' fora do seu plano ({PLAN_FILE})"


def junit_classname(mission: str) -> str:
    """Nome que liga o teste à missão no relatório JUnit (`reports/junit.xml`)."""
    return f"Missão {mission}: {MISSIONS[mission]}"
