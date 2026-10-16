def get_tool_execution_summary(messages: list) -> dict:
    """Separate requested tools, successful results, and tool errors."""

    requested_tools = []
    successful_tools = []
    failed_tools = []

    for message in messages:
        for tool_call in getattr(message, "tool_calls", []):
            name = tool_call.get("name")
            if name and name not in requested_tools:
                requested_tools.append(name)

        if getattr(message, "type", None) == "tool":
            name = getattr(message, "name", None)
            if not name:
                continue

            # LangChain ToolMessage can mark an execution error with status="error".
            status = getattr(message, "status", "success")

            if status == "error":
                if name not in failed_tools:
                    failed_tools.append(name)
            elif name not in successful_tools:
                successful_tools.append(name)

    return {
        "requested_tools": requested_tools,
        "successful_tools": successful_tools,
        "failed_tools": failed_tools,
    }


def get_tool_results(messages: list) -> list[dict]:
    """Extract tool names and their raw returned content from graph messages."""

    results = []

    for message in messages:
        if getattr(message, "type", None) != "tool":
            continue

        results.append(
            {
                "tool": getattr(message, "name", None),
                "content": getattr(message, "content", None),
                "status": getattr(message, "status", "success"),
            }
        )

    return results

