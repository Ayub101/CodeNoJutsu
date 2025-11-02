# main.py
import argparse
import sys
import traceback
from typing import Any
from agent.graph import agent


def run_agent(user_prompt: str, recursion_limit: int = 100) -> Any:
    """
    Run the LangGraph agent and return the final state/result.

    This function is designed to be imported and called from other code
    (e.g., the Streamlit UI). The agent is expected to write files into
    the `generated_project/` folder using your write_file tool.
    """
    result = agent.invoke(
        {"user_prompt": user_prompt},
        {"recursion_limit": recursion_limit}
    )
    return result


def main_cli():
    """Preserve CLI behavior when this file is executed directly."""
    parser = argparse.ArgumentParser(description="Run engineering project planner")
    parser.add_argument("user_prompt", nargs="?", help="Project prompt (if not provided, will ask interactively)")
    parser.add_argument("--recursion-limit", "-r", type=int, default=100,
                        help="Recursion limit for processing (default: 100)")

    args = parser.parse_args()

    try:
        if not args.user_prompt:
            args.user_prompt = input("Enter your project prompt: ")

        result = run_agent(args.user_prompt, recursion_limit=args.recursion_limit)
        print("Final State:", result)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        traceback.print_exc()
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main_cli()
