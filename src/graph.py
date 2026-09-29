"""
PECA-Guard Dual Agent - Real LangGraph
Workflow: Goal -> Decide -> Act -> Observe -> Continue/Complete + 1 Retry
Model: openai/gpt-oss-20b
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import TypedDict
from langgraph.graph import StateGraph, END
from src.agents.sentinel_agent import analyze_with_sentinel
from src.agents.enforcer_agent import enforce_legal

class AgentState(TypedDict):
    user_input: str
    groq_client: object
    agent1_output: dict
    agent2_output: dict
    retry_count: int
    final_answer: str

def sentinel_node(state: AgentState):
    print("🛡️ [Sentinel] Goal: Detect cybercrime")
    result = analyze_with_sentinel(state["user_input"], state.get("groq_client"))
    return {"agent1_output": result, "retry_count": 0}

def enforcer_node(state: AgentState):
    print("⚖️ [Enforcer] Goal: Fetch punishment")
    sentinel_out = state["agent1_output"]
    retry = state.get("retry_count", 0) > 0
    result = enforce_legal(sentinel_out, state.get("groq_client"), retry=retry)
    return {"agent2_output": result, "final_answer": result["text"]}

def should_retry(state: AgentState):
    score = state["agent2_output"]["score"]
    detected = state["agent1_output"]["detected"]
    retry_count = state.get("retry_count", 0)
    if score < 0.35 and detected and retry_count == 0:
        return "retry"
    return "end"

def retry_node(state: AgentState):
    return {"retry_count": 1}

workflow = StateGraph(AgentState)
workflow.add_node("sentinel", sentinel_node)
workflow.add_node("enforcer", enforcer_node)
workflow.add_node("retry_tracker", retry_node)
workflow.set_entry_point("sentinel")
workflow.add_edge("sentinel", "enforcer")
workflow.add_conditional_edges("enforcer", should_retry, {"retry": "retry_tracker", "end": END})
workflow.add_edge("retry_tracker", "enforcer")
app_graph = workflow.compile()

def run_dual_agents(user_input: str, groq_client=None):
    initial_state = {
        "user_input": user_input,
        "groq_client": groq_client,
        "agent1_output": {},
        "agent2_output": {},
        "retry_count": 0,
        "final_answer": ""
    }
    final_state = app_graph.invoke(initial_state)
    return {
        "agent1_output": final_state["agent1_output"],
        "agent2_output": final_state["agent2_output"],
        "final_answer": final_state["final_answer"]
    }
