import pytest
from tools import (
    check_service_health,
    check_data_quality,
    check_deployment_history,
)


def test_latency_scenario():
    result = check_service_health.invoke({"scenario": "latency_spike"})
    assert result["p95_latency_ms"] == 1800
    assert result["status"] == "degraded"


def test_data_quality_scenario():
    result = check_data_quality.invoke({"scenario": "data_quality"})
    assert result["missing_pct"] == 18.0
    assert result["schema_violations"] == 12


def test_healthy_scenario():
    result = check_service_health.invoke({"scenario": "healthy"})
    assert result["status"] == "healthy"
    assert result["error_rate_pct"] == 0.1


def test_unknown_scenario_rejected():
    with pytest.raises(ValueError):
        check_service_health.invoke({"scenario": "unknown"})