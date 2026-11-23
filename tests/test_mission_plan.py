import json
from pathlib import Path

import pytest

from tests.support.missions import MISSIONS, PlanError, junit_classname, mission_skip_reason, planned_missions


def write_plan(root: Path, content: str) -> None:
    (root / ".vaga-viva").mkdir()
    (root / ".vaga-viva" / "plan.json").write_text(content, encoding="utf-8")


def test_sem_plano_todas_as_missoes_rodam(tmp_path):
    assert planned_missions(tmp_path) is None
    assert all(mission_skip_reason(mission, tmp_path) is None for mission in MISSIONS)


def test_missao_fora_do_plano_e_ignorada_com_o_motivo_padrao(tmp_path):
    write_plan(tmp_path, json.dumps({"archetype": "python-fastapi", "missions": ["patients-api", "persistence"]}))

    assert mission_skip_reason("patients-api", tmp_path) is None
    assert mission_skip_reason("bug-hunt", tmp_path) == "Missão 'bug-hunt' fora do seu plano (.vaga-viva/plan.json)"


def test_plano_com_json_malformado_falha_com_mensagem_clara(tmp_path):
    write_plan(tmp_path, '{"missions": [')

    with pytest.raises(PlanError, match=r"Não foi possível ler \.vaga-viva/plan\.json"):
        planned_missions(tmp_path)


@pytest.mark.parametrize(
    "content", ['{"archetype": "python-fastapi"}', '{"missions": "patients-api"}', '{"missions": [1]}', "[]"]
)
def test_plano_sem_a_lista_missions_falha_com_mensagem_clara(tmp_path, content):
    write_plan(tmp_path, content)

    with pytest.raises(PlanError, match='precisa ter a lista "missions"'):
        planned_missions(tmp_path)


def test_classname_do_junit_tem_o_id_e_o_titulo_da_missao():
    assert junit_classname("patients-api") == "Missão patients-api: Cadastro de pacientes"
