"""Ganchos do Vaga Viva no pytest: plano de missões, opção --mission e relatório JUnit por missão."""

import pytest
from _pytest.junitxml import xml_key

from tests.support.missions import MISSIONS, PlanError, junit_classname, mission_skip_reason

_missions_by_test: dict[str, str] = {}
_config: pytest.Config | None = None


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--mission",
        metavar="ID",
        default=None,
        help="roda só os testes de uma missão, por exemplo: --mission patients-api",
    )


def pytest_configure(config: pytest.Config) -> None:
    global _config
    _config = config


def _mission_of(item: pytest.Item) -> str | None:
    marker = item.get_closest_marker("mission")
    if marker is None:
        return None
    mission = marker.args[0] if marker.args else None
    if mission not in MISSIONS:
        raise pytest.UsageError(
            f"{item.nodeid}: missão desconhecida {mission!r} em @pytest.mark.mission. Use um destes ids: "
            + ", ".join(MISSIONS)
        )
    return mission


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    only = config.getoption("mission")
    if only is not None and only not in MISSIONS:
        raise pytest.UsageError(f"Missão desconhecida '{only}' em --mission. Use um destes ids: {', '.join(MISSIONS)}")
    selected: list[pytest.Item] = []
    deselected: list[pytest.Item] = []
    for item in items:
        mission = _mission_of(item)
        if only is not None and mission != only:
            deselected.append(item)
            continue
        selected.append(item)
        if mission is None:
            continue
        _missions_by_test[item.nodeid] = mission
        try:
            reason = mission_skip_reason(mission)
        except PlanError as error:
            raise pytest.UsageError(str(error)) from error
        if reason is not None:
            item.add_marker(pytest.mark.skip(reason=reason))
    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """Grava `classname="Missão <id>: <título>"` no relatório JUnit, inclusive nos testes ignorados."""
    mission = _missions_by_test.get(report.nodeid)
    xml = _config.stash.get(xml_key, None) if _config is not None else None
    if mission is not None and xml is not None:
        xml.node_reporter(report).attrs["classname"] = junit_classname(mission)
