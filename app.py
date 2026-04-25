"""
Agent Arena - Web Dashboard
A visual interface to watch the multi-agent game loop in action.
"""

import json
import time
import threading
import queue
from flask import Flask, render_template, Response, request, jsonify

app = Flask(__name__, template_folder="web/templates", static_folder="web/static")

# Global event queue for SSE (Server-Sent Events)
game_events = queue.Queue()


def emit_event(event_type, data):
    """Push an event to the SSE stream."""
    game_events.put({"type": event_type, "data": data})


def run_game_simulation(mission):
    """Run the multi-agent game loop and emit events for each step."""
    emit_event("game_start", {"mission": mission})
    time.sleep(1)

    agent_details = {
        "planner": {
            "name": "Planner Agent",
            "icon": "brain",
            "color": "#a78bfa",
            "actions": [
                "Analyzing mission objectives and constraints...",
                "Identifying key milestones and dependencies...",
                "Drafting resource acquisition and allocation plan.",
            ],
        },
        "researcher": {
            "name": "Researcher Agent",
            "icon": "search",
            "color": "#60a5fa",
            "actions": [
                "Querying ChromaDB vector memory for past strategies...",
                "Searching MCP knowledge base for relevant data...",
                "Discovered low-cost API resources and market intel.",
            ],
        },
        "coder": {
            "name": "Coder Agent",
            "icon": "code",
            "color": "#34d399",
            "actions": [
                "Synthesizing implementation logic from plan...",
                "Compiling and deploying build artifacts...",
                "Deployment successful. Running integration checks.",
            ],
        },
        "critic": {
            "name": "Critic Agent",
            "icon": "shield",
            "color": "#f472b6",
            "actions": [
                "Evaluating phase output against mission KPIs...",
                "Scoring resource efficiency and goal alignment...",
                "Generating critique report and next-turn recommendation.",
            ],
        },
    }

    max_turns = 3
    for turn in range(1, max_turns + 1):
        emit_event("turn_start", {"turn": turn, "max_turns": max_turns})
        time.sleep(0.8)

        for agent_key in ["planner", "researcher", "coder", "critic"]:
            agent = agent_details[agent_key]
            emit_event("agent_start", {
                "turn": turn,
                "agent": agent_key,
                "name": agent["name"],
                "icon": agent["icon"],
                "color": agent["color"],
            })
            time.sleep(0.6)

            # Stream each action step
            for i, action in enumerate(agent["actions"]):
                emit_event("agent_action", {
                    "turn": turn,
                    "agent": agent_key,
                    "step": i + 1,
                    "total_steps": len(agent["actions"]),
                    "action": action,
                })
                time.sleep(0.7)

            # Final result
            if agent_key == "planner":
                result = f"Turn {turn}: Strategic plan drafted with {turn + 2} milestones."
            elif agent_key == "researcher":
                result = f"Turn {turn}: Retrieved {turn * 4} relevant knowledge chunks from vector DB."
            elif agent_key == "coder":
                result = f"Turn {turn}: Version {turn}.0 deployed successfully. All tests passing."
            else:
                if turn >= max_turns:
                    result = f"Turn {turn}: Mission objectives met. Recommending: MISSION ACCOMPLISHED."
                else:
                    result = f"Turn {turn}: Progress satisfactory. Recommending: CONTINUE to next turn."

            emit_event("agent_complete", {
                "turn": turn,
                "agent": agent_key,
                "name": agent["name"],
                "result": result,
                "decision": "mission_accomplished" if (agent_key == "critic" and turn >= max_turns) else "continue",
            })
            time.sleep(0.5)

        # Memory storage event
        emit_event("memory_store", {
            "turn": turn,
            "entries": [
                f"Episodic memory: Turn {turn} strategy and outcomes stored.",
                f"Semantic memory: {turn * 3} new concepts indexed in ChromaDB.",
            ]
        })
        time.sleep(0.5)

        emit_event("turn_end", {
            "turn": turn,
            "status": "mission_accomplished" if turn >= max_turns else "continue",
        })
        time.sleep(0.8)

    emit_event("game_end", {
        "mission": mission,
        "total_turns": max_turns,
        "status": "Mission Accomplished!",
    })


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start_game():
    """Start a new game simulation in a background thread."""
    data = request.json or {}
    mission = data.get("mission", "Build a self-sustaining tech startup in 30 turns")

    # Clear any old events
    while not game_events.empty():
        game_events.get()

    thread = threading.Thread(target=run_game_simulation, args=(mission,), daemon=True)
    thread.start()
    return jsonify({"status": "started", "mission": mission})


@app.route("/stream")
def stream():
    """SSE endpoint to stream game events to the frontend."""
    def generate():
        while True:
            try:
                event = game_events.get(timeout=30)
                yield f"data: {json.dumps(event)}\n\n"
                if event["type"] == "game_end":
                    break
            except queue.Empty:
                # Send heartbeat to keep connection alive
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"

    return Response(generate(), mimetype="text/event-stream")


if __name__ == "__main__":
    print("\n  Agent Arena Dashboard")
    print("  Open http://localhost:5000 in your browser\n")
    app.run(debug=False, port=5000)
