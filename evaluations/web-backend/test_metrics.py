"""
Test script to verify custom metrics work correctly.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluations.metrics import PracticePlanQuality, ResponseCompleteness


def test_practice_plan_quality():
    """Test the PracticePlanQuality metric."""
    print("=" * 80)
    print("Testing PracticePlanQuality Metric")
    print("=" * 80)
    print()

    metric = PracticePlanQuality()

    # Test case 1: Valid practice plan
    valid_response = """
    Based on your recent sessions, here's a practice plan:

    {
        "focus_area": "Pitch Accuracy",
        "current_score": 72.5,
        "suggested_scale": "C major",
        "suggested_scale_type": "major",
        "session_target": "15-20 minutes",
        "exercises": [
            "Slow scale practice at 60 BPM",
            "Focus on precise finger placement",
            "Use a tuner to verify each note"
        ]
    }

    Try this plan in your next session!
    """

    result = metric.score(output=valid_response)
    print(f"Test 1 - Valid Practice Plan:")
    print(f"  Score: {result.value}")
    print(f"  Reason: {result.reason}")
    print()

    # Test case 2: Missing fields
    invalid_response = """
    {
        "focus_area": "Pitch Accuracy",
        "current_score": 72.5
    }
    """

    result = metric.score(output=invalid_response)
    print(f"Test 2 - Missing Fields:")
    print(f"  Score: {result.value}")
    print(f"  Reason: {result.reason}")
    print()

    # Test case 3: No practice plan
    no_plan_response = "Your progress looks good! Keep practicing."

    result = metric.score(output=no_plan_response)
    print(f"Test 3 - No Practice Plan:")
    print(f"  Score: {result.value}")
    print(f"  Reason: {result.reason}")
    print()


def test_response_completeness():
    """Test the ResponseCompleteness metric."""
    print("=" * 80)
    print("Testing ResponseCompleteness Metric")
    print("=" * 80)
    print()

    metric = ResponseCompleteness()

    # Test case 1: Complete and actionable
    complete_response = """
    Great question! Based on your recent practice sessions, I recommend focusing
    on timing stability. Your pitch accuracy is strong at 85%, but timing could
    improve. Try practicing with a metronome at 80 BPM and gradually increase
    the tempo. Work on scales for 15 minutes daily.
    """

    result = metric.score(output=complete_response)
    print(f"Test 1 - Complete and Actionable:")
    print(f"  Score: {result.value}")
    print(f"  Reason: {result.reason}")
    print()

    # Test case 2: Too short
    short_response = "Looks good!"

    result = metric.score(output=short_response)
    print(f"Test 2 - Too Short:")
    print(f"  Score: {result.value}")
    print(f"  Reason: {result.reason}")
    print()

    # Test case 3: Contains error
    error_response = "I apologize, but I encountered an issue processing your request."

    result = metric.score(output=error_response)
    print(f"Test 3 - Contains Error:")
    print(f"  Score: {result.value}")
    print(f"  Reason: {result.reason}")
    print()

    # Test case 4: Empty response
    empty_response = ""

    result = metric.score(output=empty_response)
    print(f"Test 4 - Empty Response:")
    print(f"  Score: {result.value}")
    print(f"  Reason: {result.reason}")
    print()


if __name__ == "__main__":
    test_practice_plan_quality()
    print()
    test_response_completeness()
    print()
    print("=" * 80)
    print("✅ All metric tests completed!")
    print("=" * 80)
