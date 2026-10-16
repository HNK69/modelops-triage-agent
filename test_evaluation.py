from evaluation import evaluate_severity
from evaluation import evaluate_tool_evidence

def test_critical_severity():
    service = {"error_rate_pct": 10, "p95_latency_ms": 100}
    data = {"missing_pct": 0, "schema_violations": 0}

    assert evaluate_severity(service, data) == "critical"


def test_high_severity_from_data_quality():
    service = {"error_rate_pct": 0.1, "p95_latency_ms": 100}
    data = {"missing_pct": 18, "schema_violations": 12}

    assert evaluate_severity(service, data) == "high"


def test_medium_severity():
    service = {"error_rate_pct": 2, "p95_latency_ms": 200}
    data = {"missing_pct": 0.5, "schema_violations": 0}

    assert evaluate_severity(service, data) == "medium"


def test_low_severity():
    service = {"error_rate_pct": 0.1, "p95_latency_ms": 120}
    data = {"missing_pct": 0.2, "schema_violations": 0}

    assert evaluate_severity(service, data) == "low"

def test_latency_threshold_is_high():
    service = {"error_rate_pct": 0.1, "p95_latency_ms": 1500}
    data = {"missing_pct": 0.2, "schema_violations": 0}

    assert evaluate_severity(service, data) == "high"


def test_just_below_medium_threshold_is_low():
    service = {"error_rate_pct": 0.9, "p95_latency_ms": 499}
    data = {"missing_pct": 4.9, "schema_violations": 0}

    assert evaluate_severity(service, data) == "low"


def test_evaluates_severity_from_tool_results():
    tool_results = [
        {
            "tool": "check_service_health",
            "content": '{"status": "degraded", "error_rate_pct": 1.2, '
                       '"p95_latency_ms": 1800, "requests_per_min": 1200}',
            "status": "success",
        },
        {
            "tool": "check_data_quality",
            "content": '{"missing_pct": 0.5, "schema_violations": 0, '
                       '"anomalies": []}',
            "status": "success",
        },
    ]

    assert evaluate_tool_evidence(tool_results) == "high"


def test_rejects_missing_required_evidence():
    tool_results = [
        {
            "tool": "check_service_health",
            "content": '{"error_rate_pct": 1.2, "p95_latency_ms": 1800}',
            "status": "success",
        }
    ]

    import pytest

    with pytest.raises(ValueError, match="both required"):
        evaluate_tool_evidence(tool_results)


def test_rejects_failed_required_tool():
    tool_results = [
        {
            "tool": "check_service_health",
            "content": "Unknown scenario",
            "status": "error",
        },
        {
            "tool": "check_data_quality",
            "content": '{"missing_pct": 0.5, "schema_violations": 0}',
            "status": "success",
        },
    ]

    import pytest

    with pytest.raises(ValueError, match="both required"):
        evaluate_tool_evidence(tool_results)


import pytest


def test_rejects_malformed_json():
    tool_results = [
        {
            "tool": "check_service_health",
            "content": '{"error_rate_pct": 1.2,',
            "status": "success",
        },
        {
            "tool": "check_data_quality",
            "content": '{"missing_pct": 0.5, "schema_violations": 0}',
            "status": "success",
        },
    ]

    with pytest.raises(ValueError, match="invalid JSON"):
        evaluate_tool_evidence(tool_results)


def test_rejects_missing_metric_field():
    tool_results = [
        {
            "tool": "check_service_health",
            "content": '{"error_rate_pct": 1.2}',
            "status": "success",
        },
        {
            "tool": "check_data_quality",
            "content": '{"missing_pct": 0.5, "schema_violations": 0}',
            "status": "success",
        },
    ]

    with pytest.raises(ValueError, match="missing required field"):
        evaluate_tool_evidence(tool_results)


def test_rejects_non_numeric_metric():
    tool_results = [
        {
            "tool": "check_service_health",
            "content": '{"error_rate_pct": "high", "p95_latency_ms": 1800}',
            "status": "success",
        },
        {
            "tool": "check_data_quality",
            "content": '{"missing_pct": 0.5, "schema_violations": 0}',
            "status": "success",
        },
    ]

    with pytest.raises(ValueError, match="must be numeric"):
        evaluate_tool_evidence(tool_results)


def test_rejects_duplicate_tool_results():
    tool_results = [
        {
            "tool": "check_service_health",
            "content": '{"error_rate_pct": 1.2, "p95_latency_ms": 1800}',
            "status": "success",
        },
        {
            "tool": "check_service_health",
            "content": '{"error_rate_pct": 0.1, "p95_latency_ms": 120}',
            "status": "success",
        },
        {
            "tool": "check_data_quality",
            "content": '{"missing_pct": 0.5, "schema_violations": 0}',
            "status": "success",
        },
    ]

    with pytest.raises(ValueError, match="Duplicate tool result"):
        evaluate_tool_evidence(tool_results)


def test_rejects_non_finite_metric():
    tool_results = [
        {
            "tool": "check_service_health",
            "content": '{"error_rate_pct": NaN, "p95_latency_ms": 1800}',
            "status": "success",
        },
        {
            "tool": "check_data_quality",
            "content": '{"missing_pct": 0.5, "schema_violations": 0}',
            "status": "success",
        },
    ]

    with pytest.raises(ValueError, match="must be finite"):
        evaluate_tool_evidence(tool_results)


def test_rejects_negative_metric():
    tool_results = [
        {
            "tool": "check_service_health",
            "content": '{"error_rate_pct": -1, "p95_latency_ms": 1800}',
            "status": "success",
        },
        {
            "tool": "check_data_quality",
            "content": '{"missing_pct": 0.5, "schema_violations": 0}',
            "status": "success",
        },
    ]

    with pytest.raises(ValueError, match="cannot be negative"):
        evaluate_tool_evidence(tool_results)
