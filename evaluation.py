def evaluate_severity(service: dict, data_quality: dict) -> str:
    """Assign severity using explicit thresholds for simulated incidents."""

    error_rate = service["error_rate_pct"]
    latency = service["p95_latency_ms"]
    missing_pct = data_quality["missing_pct"]
    schema_violations = data_quality["schema_violations"]

    if error_rate >= 10 or latency >= 3000:
        return "critical"

    if (
        error_rate >= 5
        or latency >= 1500
        or missing_pct >= 15
        or schema_violations >= 10
    ):
        return "high"

    if (
        error_rate >= 1
        or latency >= 500
        or missing_pct >= 5
        or schema_violations > 0
    ):
        return "medium"

    return "low"
