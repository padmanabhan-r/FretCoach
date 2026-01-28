"""
Evaluation script for FretCoach Hub LangGraph Agent.

This script evaluates the agent using production traces stored in Opik dataset.
It measures response quality, helpfulness, and practice plan generation accuracy.
"""
import sys
from pathlib import Path

# Add web-backend directory to path for imports
web_backend_path = Path(__file__).parent.parent.parent / "web" / "web-backend"
sys.path.insert(0, str(web_backend_path))

# Add current directory for local imports
sys.path.insert(0, str(Path(__file__).parent))

from opik import Opik
from opik.evaluation import evaluate
from opik.evaluation.metrics import Hallucination, AnswerRelevance

# Import workflow and custom metrics
from langgraph_workflow import invoke_workflow
from metrics import PracticePlanQuality, ResponseCompleteness


def evaluation_task(dataset_item: dict) -> dict:
    """
    Execute the agent on a dataset item and return results.

    Args:
        dataset_item: Item from the Opik dataset containing:
            - input: Agent state with messages, user_id, thread_id
            - expected_output: Original production response (for reference)

    Returns:
        dict with:
            - input: User's query (last message)
            - output: Agent's new response
            - reference: Expected output from production
            - context: Any tool call results
    """
    try:
        # Extract input data
        input_data = dataset_item.get("input", {})
        messages = input_data.get("messages", [])
        user_id = input_data.get("user_id", "default_user")

        if not messages:
            return {
                "input": "No input message found",
                "output": "Error: No input message",
                "reference": "",
                "context": [],
                "error": "No messages in dataset item"
            }

        # Extract the user's query (look for human message, fallback to first message)
        user_query = None
        for msg in messages:
            if msg.get("type") == "human":
                user_query = msg.get("content", "")
                break

        # Fallback: if no human message found, use first message content
        if not user_query and messages:
            user_query = messages[0].get("content", "")

        # Check if this looks like an AI greeting (not a real user query)
        is_ai_greeting = "I'm your AI practice coach" in user_query if user_query else False

        if not user_query:
            return {
                "input": "No user query found",
                "output": "Error: No user query",
                "reference": "",
                "context": [],
                "error": "No human message found"
            }

        # Convert to format expected by invoke_workflow
        formatted_messages = [{"role": "user", "content": user_query}]

        # Invoke the workflow (no thread_id for fresh evaluation)
        result = invoke_workflow(
            messages=formatted_messages,
            user_id=user_id,
            thread_id=None,  # Fresh conversation
            use_fallback=False
        )

        # Extract response and tool results
        response = result.get("response", "")
        tool_calls = result.get("tool_calls", [])

        # Build context from tool results
        context = []
        for tool_call in tool_calls:
            context.append(f"Tool: {tool_call.get('tool', 'unknown')}")
            tool_result = tool_call.get('result', '')
            if isinstance(tool_result, str) and len(tool_result) > 200:
                tool_result = tool_result[:200] + "..."
            context.append(f"Result: {tool_result}")

        # Get expected output (reference)
        expected_output = dataset_item.get("expected_output", {})
        if isinstance(expected_output, dict):
            # The expected_output has 'messages' key with the AI's response
            messages_list = expected_output.get("messages", [])
            if messages_list and isinstance(messages_list, list):
                # Get the last AI message as the reference response
                for msg in reversed(messages_list):
                    if msg.get("type") == "ai" or msg.get("role") == "assistant":
                        reference = msg.get("content", str(expected_output))
                        break
                else:
                    reference = str(messages_list[-1]) if messages_list else str(expected_output)
            else:
                reference = str(expected_output)
        else:
            reference = str(expected_output)

        # Mark if this is an AI greeting (not a real user query)
        is_ai_greeting = "I'm your AI practice coach" in user_query if user_query else False

        return {
            "input": user_query,
            "output": response,
            "reference": reference,
            "context": context,
            "is_ai_greeting": is_ai_greeting  # Flag for metrics that need to skip AI greetings
        }

    except Exception as e:
        user_query = dataset_item.get("input", {}).get("messages", [{}])[-1].get("content", "Unknown")
        is_ai_greeting = "I'm your AI practice coach" in user_query if user_query else False
        return {
            "input": user_query,
            "output": f"Error processing request: {str(e)}",
            "reference": "",
            "context": [],
            "error": str(e),
            "is_ai_greeting": is_ai_greeting
        }


def main():
    """Run the evaluation experiment."""
    print("=" * 80)
    print("FretCoach Hub AI Coach Agent Evaluation")
    print("=" * 80)
    print()

    # Initialize Opik client
    client = Opik()

    # Get the dataset
    dataset_name = "FretCoach Hub AI Coach Chat"
    print(f"📊 Loading dataset: {dataset_name}")

    try:
        dataset = client.get_dataset(name=dataset_name)
        items = dataset.get_items()
        print(f"✅ Dataset loaded: {len(items)} items")
        print()
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        print("\nMake sure:")
        print("  1. OPIK_API_KEY is set")
        print("  2. OPIK_WORKSPACE is set")
        print(f"  3. Dataset '{dataset_name}' exists in Opik")
        return

    # Define metrics
    print("📏 Evaluation metrics:")
    print("  1. Answer Relevance - How relevant is the response to the query")
    print("  2. Hallucination - Whether the response contains unsupported claims")
    print("  3. Practice Plan Quality - Validates practice plan JSON structure")
    print("  4. Response Completeness - Checks if response is helpful and actionable")
    print()

    metrics = [
        AnswerRelevance(),
        Hallucination(),
        PracticePlanQuality(),
        ResponseCompleteness()
    ]

    # Run evaluation
    experiment_name = "FretCoach Hub Agent Evaluation v1"
    print(f"🚀 Starting evaluation experiment: {experiment_name}")
    print("   This will test the agent on all 10 production traces...")
    print()

    try:
        results = evaluate(
            experiment_name=experiment_name,
            dataset=dataset,
            task=evaluation_task,
            scoring_metrics=metrics
        )

        print()
        print("=" * 80)
        print("✅ Evaluation Complete!")
        print("=" * 80)
        print(f"   Experiment ID: {results.experiment_id if hasattr(results, 'experiment_id') else 'N/A'}")
        print()
        print("📊 View results in Opik dashboard:")
        print("   - Navigate to Experiments")
        print(f"   - Open experiment: {experiment_name}")
        print()
        print("Results summary:")
        print(f"   Total items evaluated: {len(items)}")
        print()

    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
