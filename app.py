
import argparse  # Reads command-line options, e.g. --scenario healthy.
import os  # Reads environment variables such as GOOGLE_API_KEY.

from dotenv import load_dotenv  # Loads settings from the local .env file.
from langchain_google_genai import ChatGoogleGenerativeAI  # Connects LangChain to Gemini.
from langgraph.graph import START, END, MessagesState, StateGraph  # Core LangGraph graph components.
from langgraph.prebuilt import ToolNode, tools_condition  # Executes tools and routes based on tool calls.
from evaluation import evaluate_tool_evidence
from evidence import get_tool_execution_summary, get_tool_results
from scenarios import SCENARIOS
from tools import DIAGNOSTIC_TOOLS

load_dotenv()  # Makes .env variables available through os.getenv(); does not print secrets.

SYSTEM_PROMPT = """
You are a ModelOps incident triage engineer investigating SIMULATED data.

Investigate the supplied scenario using diagnostic tools.

Required diagnostics:
- Always call check_service_health.
- Always call check_data_quality before producing the final report.
- Call check_deployment_history when deployment history may help explain the incident.

Use returned tool results as evidence. Never invent missing results.

Rules:
- Treat tool results as observed evidence, not assumptions.
- Never invent metrics, deployments, or tool results.
- Distinguish confirmed observations from hypotheses.
- A healthy service must not be reported as an incident without evidence.
- Do not execute remediation or claim to have changed any system.
- A deployment preceding an incident is correlation, not proof of causation.
- Do not claim a root cause is confirmed unless evidence directly supports it.
- Recommend rollback as a conditional option when a deployment is a plausible cause; consider validating the change and checking additional telemetry first.
- Use low confidence when evidence supports only a hypothesis, medium when multiple observations support it, and high only when the cause is strongly verified.
- The deterministic rule-based severity printed by the application is authoritative; do not present a conflicting severity as the final severity.

Produce a report with:
1. Incident summary
2. Observed evidence
3. Likely causes and supporting evidence
4. Confidence and justification
5. Recommended next diagnostic or remediation steps

All data is simulated, not live production telemetry.
"""  # Instructions guiding the model's investigation and report format.

MODEL_NAME = "gemini-3.1-flash-lite"  # Gemini model identifier; we will verify API access by running it.


def build_graph():
    """Create and compile the diagnostic agent's workflow."""

    # Fail early with a useful error if the API key is unavailable.
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is missing. Check your local .env file.")

    # Create the Gemini model client.
    # temperature=0 reduces randomness; it does not guarantee identical outputs.
    # bind_tools tells the model which functions it may request.
    model = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0,
    ).bind_tools(DIAGNOSTIC_TOOLS)

    # A node is one step in the graph.
    # This node sends conversation history to Gemini and returns its response.
    def agent(state: MessagesState):
        response = model.invoke(
            [{"role": "system", "content": SYSTEM_PROMPT}]
            + state["messages"]  # Preserve the user's question and previous tool results.
        )
        return {"messages": [response]}  # Add the new model response to graph state.

    # StateGraph coordinates the workflow; MessagesState stores conversation messages.
    graph = StateGraph(MessagesState)

    graph.add_node("agent", agent)  # LLM reasoning and tool-selection step.
    graph.add_node("tools", ToolNode(DIAGNOSTIC_TOOLS))  # Executes requested diagnostic functions.

    graph.add_edge(START, "agent")  # Every investigation starts with the model.
    graph.add_conditional_edges(
        "agent", tools_condition
    )  # Tool call present -> tools; otherwise -> END.
    graph.add_edge("tools", "agent")  # Feed tool results back to Gemini for further reasoning.
    # This creates the agent loop: model -> tools -> model, repeated when needed.

    return graph.compile()  # Validate and prepare the graph for execution.


def main():
    # argparse lets us choose a scenario without editing the source code.
    parser = argparse.ArgumentParser(
        description="Investigate a simulated ModelOps incident."
    )
    parser.add_argument(
        "--scenario",
        choices=list(SCENARIOS),  # Reject scenario names that do not exist.
        default="latency_spike",  # Use this case if the user provides no option.
        help="Select a simulated incident scenario.",
    )
    parser.add_argument(
        "--show-evidence",
        action="store_true",
        help="Display raw diagnostic tool results.",
    )
    args = parser.parse_args()

    app = build_graph()  # Construct the agent workflow.

    # Start a new investigation with the selected scenario in the user message.
    result = app.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Investigate the '{args.scenario}' scenario. "
                        "Determine which diagnostics are necessary."
                    ),
                }
            ]
        },
        config={"recursion_limit": 12},  # Safety limit on graph execution steps.
    )

    # Print the final model response. Tool execution details remain in graph state.
    print(f"\nScenario: {args.scenario}")
    print("=" * 60)

    tool_results = get_tool_results(result["messages"])
    tool_summary = get_tool_execution_summary(result["messages"])

    print("Diagnostic tool execution:")
    print(f"  Requested: {tool_summary['requested_tools']}")
    print(f"  Returned results: {tool_summary['successful_tools']}")
    print(f"  Errors: {tool_summary['failed_tools']}")
    print("-" * 60)

    try:
        severity = evaluate_tool_evidence(tool_results)
    except (ValueError, KeyError, TypeError) as exc:
        severity = None
        print(f"Rule-based severity: UNAVAILABLE ({exc})")
    else:
        print(f"Rule-based severity: {severity.upper()}")

    print("Note: This severity is calculated by deterministic rules.")
    print("-" * 60)

    if args.show_evidence:
        print("Evidence trace:")
        for item in tool_results:
            print(f"  Tool: {item['tool']}")
            print(f"  Status: {item['status']}")
            print(f"  Result: {item['content']}")
            print("-" * 40)

    final_message = result["messages"][-1]
    for block in final_message.content:
        if isinstance(block, dict) and block.get("type") == "text":
            print(block["text"])
        elif isinstance(block, str):
            print(block)

if __name__ == "__main__":
    main()  # Run main() only when this file is executed directly.
