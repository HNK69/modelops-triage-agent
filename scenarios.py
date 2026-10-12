SCENARIOS = {
    "latency_spike": {
        "service": {"status": "degraded", "error_rate_pct": 1.2,
                    "p95_latency_ms": 1800, "requests_per_min": 1200},
        "data_quality": {"missing_pct": 0.5, "schema_violations": 0,
                         "anomalies": []},
        "deployments": [{"version": "v2.3", "minutes_ago": 15,
                         "change": "Updated inference dependency"}],
    },
    "data_quality": {
        "service": {"status": "degraded", "error_rate_pct": 8.5,
                    "p95_latency_ms": 450, "requests_per_min": 900},
        "data_quality": {"missing_pct": 18.0, "schema_violations": 12,
                         "anomalies": ["Unexpected null values", "Invalid feature type"]},
        "deployments": [{"version": "v2.2", "minutes_ago": 180,
                         "change": "No relevant changes recorded"}],
    },
    "healthy": {
        "service": {"status": "healthy", "error_rate_pct": 0.1,
                    "p95_latency_ms": 120, "requests_per_min": 1000},
        "data_quality": {"missing_pct": 0.2, "schema_violations": 0,
                         "anomalies": []},
        "deployments": [],
    },
}