from typing import Annotated, TypedDict, Sequence
import operator
import time

# State definition for LangGraph
class GameState(TypedDict):
    mission: str
    turn: int
    messages: Annotated[Sequence[str], operator.add]
    status: str

# Node functions
def planner_node(state: GameState):
    print(f"[Turn {state['turn']}] 🧠 Planner Agent: Breaking down mission '{state['mission']}'...")
    time.sleep(1)
    return {
        "messages": [f"Turn {state['turn']} Planner: Drafted resource acquisition plan."],
        "status": "planning_done"
    }

def researcher_node(state: GameState):
    print(f"[Turn {state['turn']}] 🔎 Researcher Agent: Querying Vector DB & MCP knowledge base...")
    time.sleep(1)
    return {
        "messages": [f"Turn {state['turn']} Researcher: Discovered low cost API resources."],
        "status": "research_done"
    }

def coder_node(state: GameState):
    print(f"[Turn {state['turn']}] 🧑‍💻 Coder Agent: Synthesizing logic and executing implementation...")
    time.sleep(1)
    return {
        "messages": [f"Turn {state['turn']} Coder: Version {state['turn']}.0 deployed successfully."],
        "status": "execution_done"
    }

def critic_node(state: GameState):
    print(f"[Turn {state['turn']}] 🕵️ Critic Agent: Evaluating phase output against mission goals...")
    time.sleep(1)
    
    # End game after 3 simulated turns
    if state["turn"] >= 3:
        status = "mission_accomplished"
    else:
        status = "continue"
        
    return {
        "messages": [f"Turn {state['turn']} Critic: Evaluated metrics. Decision: {status}."],
        "turn": state["turn"] + 1,
        "status": status
    }

def run_game(mission: str):
    """Initializes and runs the multi-agent graph"""
    try:
        from langgraph.graph import StateGraph, END
    except ImportError:
        print("LangGraph is not natively installed. Running fallback mock text loop...")
        return process_mock_loop(mission)

    print("🚀 Compiling LangGraph Multi-Agent Workflows...\n")
    
    # Define Graph
    workflow = StateGraph(GameState)

    # Add Nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("critic", critic_node)

    # Add Directed Edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "coder")
    workflow.add_edge("coder", "critic")
    
    # Conditional edge from critic -> repeats or ends
    workflow.add_conditional_edges(
        "critic",
        lambda x: x["status"],
        {
            "continue": "planner",
            "mission_accomplished": END
        }
    )

    # Compile the graph
    app = workflow.compile()
    
    # Initial state
    inputs = {
        "mission": mission,
        "turn": 1,
        "messages": ["Game Start"],
        "status": "started"
    }
    
    final_state = app.invoke(inputs)
    return final_state

def process_mock_loop(mission: str):
    """Fallback if LangGraph is missing"""
    state: GameState = {
        "mission": mission,
        "turn": 1,
        "messages": [],
        "status": "started"
    }
    
    for _ in range(3):
        res1 = planner_node(state)
        state["messages"].extend(res1["messages"])
        
        res2 = researcher_node(state)
        state["messages"].extend(res2["messages"])
        
        res3 = coder_node(state)
        state["messages"].extend(res3["messages"])
        
        res4 = critic_node(state)
        state["messages"].extend(res4["messages"])
        state["turn"] = res4["turn"]
        state["status"] = res4["status"]
        print("-" * 40)
        
    return state
