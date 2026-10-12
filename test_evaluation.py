from evaluation import evaluate_severity


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
