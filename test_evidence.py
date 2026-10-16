
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from evidence import get_tool_execution_summary
from evidence import get_tool_results


def test_tracks_requested_and_returned_tools():
    messages = [
        HumanMessage(content="Investigate the incident"),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "check_service_health",
                    "args": {"scenario": "healthy"},
                    "id": "call_1",
                }
            ],
        ),
        ToolMessage(
            content='{"status": "healthy"}',
            name="check_service_health",
            tool_call_id="call_1",
        ),
    ]

    result = get_tool_execution_summary(messages)

    assert result["requested_tools"] == ["check_service_health"]
    assert result["successful_tools"] == ["check_service_health"]
    assert result["failed_tools"] == []


def test_requested_tool_without_result():
    messages = [
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "check_data_quality",
                    "args": {"scenario": "healthy"},
                    "id": "call_2",
                }
            ],
        )
    ]

    result = get_tool_execution_summary(messages)

    assert result["requested_tools"] == ["check_data_quality"]
    assert result["successful_tools"] == []
    assert result["failed_tools"] == []


def test_tool_execution_error():
    messages = [
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "check_service_health",
                    "args": {"scenario": "unknown"},
                    "id": "call_3",
                }
            ],
        ),
        ToolMessage(
            content="Unknown scenario",
            name="check_service_health",
            tool_call_id="call_3",
            status="error",
        ),
    ]

    result = get_tool_execution_summary(messages)

    assert result["requested_tools"] == ["check_service_health"]
    assert result["successful_tools"] == []
    assert result["failed_tools"] == ["check_service_health"]


def test_no_tools():
    messages = [HumanMessage(content="Hello")]

    result = get_tool_execution_summary(messages)

    assert result == {
        "requested_tools": [],
        "successful_tools": [],
        "failed_tools": [],
    }


def test_extracts_raw_tool_results():
    messages = [
        ToolMessage(
            content='{"status": "degraded", "p95_latency_ms": 1800}',
            name="check_service_health",
            tool_call_id="call_1",
        )
    ]

    result = get_tool_results(messages)

    assert result == [
        {
            "tool": "check_service_health",
            "content": '{"status": "degraded", "p95_latency_ms": 1800}',
            "status": "success",
        }
    ]


def test_extracts_tool_errors():
    messages = [
        ToolMessage(
            content="Unknown scenario",
            name="check_service_health",
            tool_call_id="call_2",
            status="error",
        )
    ]

    result = get_tool_results(messages)

    assert result[0]["tool"] == "check_service_health"
    assert result[0]["content"] == "Unknown scenario"
    assert result[0]["status"] == "error"

