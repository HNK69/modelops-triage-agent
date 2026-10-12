# ModelOps Triage Agent

An LLM-powered diagnostic agent that investigates simulated machine-learning service incidents using LangGraph, Gemini, and structured diagnostic tools.

## Problem

Production ML services can experience latency spikes, elevated errors, input-data quality failures, and deployment regressions. Investigating these symptoms requires collecting evidence from multiple sources.

This project demonstrates an agentic workflow for investigating such incidents and generating evidence-based reports.

## Architecture

```text
Incident Request
      |
      v
  Gemini Agent
      |
      v
 Select Diagnostic Tools
      |
      v
   ToolNode
  /    |     \
Health Data  Deployment
  \    |     /
      v
  Gemini Agent
      |
      v
 Incident Report
```

LangGraph manages the execution flow, Gemini selects tools, and Python functions return deterministic simulated evidence. The agent can execute multiple diagnostic steps before producing its report.

## Features

- Three simulated incident scenarios: latency spike, data-quality degradation, and healthy service.
- Three diagnostic tools for service health, input-data quality, and deployment history.
- LLM-driven tool selection and multi-step tool execution.
- Structured incident reports with severity, evidence, likely causes, confidence, and recommended actions.
- Environment-based configuration for API credentials.
- LangSmith tracing for inspecting model calls and tool execution.
- Automated tests for core diagnostic behavior.

## Technology Stack

- Python 3.12+
- LangGraph
- LangChain
- Google Gemini
- LangSmith
- uv
- pytest

## Setup

Prerequisites: Python 3.12+, uv, and a Google Gemini API key.

1. Clone the repository and enter the project directory.
2. Install dependencies:

   ```powershell
   uv sync
   ```

3. Create a `.env` file containing:

   ```dotenv
   GOOGLE_API_KEY=your_google_api_key
   LANGSMITH_TRACING=true
   LANGSMITH_API_KEY=your_langsmith_api_key
   LANGSMITH_PROJECT=modelops-triage-agent
   ```

   Keep `.env` private and never commit it. LangSmith tracing is optional.

## Usage

Run the simulated latency incident:

```powershell
uv run python app.py --scenario latency_spike
```

Run the data-quality incident:

```powershell
uv run python app.py --scenario data_quality
```

Check a healthy service:

```powershell
uv run python app.py --scenario healthy
```

Run automated tests:

```powershell
uv run pytest -q
```

## Diagnostic Tools

| Tool | Evidence returned |
|---|---|
| `check_service_health` | Status, error rate, p95 latency, request volume |
| `check_data_quality` | Missing-value percentage, schema violations, anomalies |
| `check_deployment_history` | Recent versions and recorded changes |

## Verification

- Diagnostic-tool smoke test passed.
- Latency-spike scenario executed successfully.
- Data-quality scenario executed successfully.
- Healthy-service scenario executed successfully.
- Four automated tests passed.
- LangSmith trace inspected, including Gemini calls and diagnostic tool execution.

## Limitations

- All service metrics and deployment records are simulated.
- Incident causes are hypotheses, not confirmed root causes.
- LLM-generated severity and confidence assessments are not independently calibrated.
- The agent recommends actions but does not execute remediation.
- No real monitoring platform or production ML service is connected.

## Future Improvements

- Add evaluation datasets and expected tool-selection tests.
- Improve evidence-grounded confidence and severity assessment.
- Add structured report validation.
- Introduce human approval for consequential actions.
- Expand observability, error handling, and deployment support.

## License

No license has been specified yet.
