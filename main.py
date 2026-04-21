import os
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Agent Arena - Multi-Agent Simulation")
    parser.add_argument("--mission", type=str, default="Build a self-sustaining tech startup in 30 turns",
                        help="The mission for the agents to accomplish")
    
    args = parser.parse_args()
    
    print(f"🎮 Starting Agent Arena")
    print(f"🎯 Mission: {args.mission}\n")
    
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "sk-your-openai-api-key":
        print("⚠️  Warning: OPENAI_API_KEY not found in environment. Using mock execution mode.\n")
    
    # Import inside to prevent execution failure if requirements are missing
    from workflows.game_loop import run_game

    # Run the orchestrator workflow
    result = run_game(args.mission)
    
    print("\n🏁 Game Finished!")
    print("Final State Messages Summary:")
    for msg in result.get("messages", []):
        print(f" - {msg}")

if __name__ == "__main__":
    main()
