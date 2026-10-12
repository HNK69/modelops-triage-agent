from langchain.tools import tool
from scenarios import SCENARIOS


def _get_scenario(scenario: str) -> dict:
    """Return a known scenario or raise a clear error."""
    if scenario not in SCENARIOS:
        raise ValueError(
            f"Unknown scenario '{scenario}'. "
            f"Choose from: {', '.join(SCENARIOS)}"
        )
    return SCENARIOS[scenario]


@tool
def check_service_health(scenario: str) -> dict:
    """Inspect service status, error rate, p95 latency, and request volume."""
    return _get_scenario(scenario)["service"]


@tool
def check_data_quality(scenario: str) -> dict:
    """Inspect missing-value percentage, schema violations, and input anomalies."""
    return _get_scenario(scenario)["data_quality"]


@tool
def check_deployment_history(scenario: str) -> dict:
    """Inspect recent model deployments and recorded changes."""
    return {"deployments": _get_scenario(scenario)["deployments"]}


DIAGNOSTIC_TOOLS = [
    check_service_health,
    check_data_quality,
    check_deployment_history,
]