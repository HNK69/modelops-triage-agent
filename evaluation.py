import json

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


def evaluate_tool_evidence(tool_results: list[dict]) -> str:
    """Calculate severity only from valid diagnostic tool evidence."""

    results_by_tool = {}

    for result in tool_results:
        if not isinstance(result, dict):
            raise ValueError("Each tool result must be a dictionary.")

        tool = result.get("tool")
        status = result.get("status")

        if status == "error":
            continue

        if status != "success":
            raise ValueError(f"Invalid tool status: {status!r}")

        if tool in results_by_tool:
            raise ValueError(f"Duplicate tool result: {tool!r}")

        results_by_tool[tool] = result.get("content")

    service = results_by_tool.get("check_service_health")
    data_quality = results_by_tool.get("check_data_quality")

    if service is None or data_quality is None:
        raise ValueError(
            "Cannot evaluate severity: successful service health "
            "and data quality results are both required."
        )

    def parse_result(name: str, content) -> dict:
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{name} returned invalid JSON."
                ) from exc

        if not isinstance(content, dict):
            raise ValueError(f"{name} must return a dictionary.")

        return content

    service = parse_result("check_service_health", service)
    data_quality = parse_result("check_data_quality", data_quality)

    required_fields = {
        "check_service_health": (
            service,
            ("error_rate_pct", "p95_latency_ms"),
        ),
        "check_data_quality": (
            data_quality,
            ("missing_pct", "schema_violations"),
        ),
    }

    for tool_name, (content, fields) in required_fields.items():
        for field in fields:
            if field not in content:
                raise ValueError(
                    f"{tool_name} is missing required field {field!r}."
                )

            value = content[field]

            # Reject booleans, strings, and other non-numeric values.
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(
                    f"{tool_name} field {field!r} must be numeric."
                )

            if not isinstance(value, (int, float)) or not (
                float("-inf") < value < float("inf")
            ):
                raise ValueError(
                    f"{tool_name} field {field!r} must be finite."
                )

            if value < 0:
                raise ValueError(
                    f"{tool_name} field {field!r} cannot be negative."
                )

    return evaluate_severity(service, data_quality)


