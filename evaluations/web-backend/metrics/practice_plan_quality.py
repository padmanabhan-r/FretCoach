"""
Custom metric to evaluate practice plan generation quality.
"""
import json
import re
from opik.evaluation.metrics import base_metric, score_result


class PracticePlanQuality(base_metric.BaseMetric):
    """
    Evaluates the quality of AI-generated practice plans.

    ONLY scores when:
    - The user's query explicitly requests a practice plan
    - The response contains a practice plan in JSON format

    For non-practice-plan queries, returns None (no score).
    """

    # Keywords that indicate a practice plan request
    PLAN_REQUEST_KEYWORDS = [
        "practice plan",
        "make a plan",
        "create a plan",
        "give me a plan",
        "build a plan",
        "suggest a plan",
        "what should i practice",
        "today's practice",
        "practice session",
        "surprise me",
    ]

    def __init__(self, name: str = "practice_plan_quality"):
        super().__init__(name=name)
        self.name = name

    def score(self, input: str, output: str, **kwargs):
        """
        Score the practice plan quality.

        Args:
            input: The user's query/input
            output: The agent's response text

        Returns:
            ScoreResult with value 0-1 and explanation, or None if not applicable
        """
        # Check if input is asking for a practice plan
        input_lower = input.lower() if input else ""
        is_plan_request = any(kw in input_lower for kw in self.PLAN_REQUEST_KEYWORDS)

        if not is_plan_request:
            # Not a practice plan request - skip scoring
            return None

        try:
            # Extract JSON from response (practice plans are in JSON format)
            json_match = re.search(r'\{[^{}]*"focus_area"[^{}]*\}', output, re.DOTALL)

            if not json_match:
                return score_result.ScoreResult(
                    name=self.name,
                    value=0.0,
                    reason="No practice plan JSON found in response"
                )

            plan_json = json_match.group(0)
            plan = json.loads(plan_json)

            # Check required fields
            required_fields = [
                "focus_area",
                "current_score",
                "suggested_scale",
                "suggested_scale_type",
                "session_target",
                "exercises"
            ]

            missing_fields = [f for f in required_fields if f not in plan]
            if missing_fields:
                return score_result.ScoreResult(
                    name=self.name,
                    value=0.3,
                    reason=f"Missing required fields: {', '.join(missing_fields)}"
                )

            # Validate field types and values
            issues = []

            # Check focus_area is non-empty string
            if not isinstance(plan["focus_area"], str) or not plan["focus_area"].strip():
                issues.append("focus_area must be non-empty string")

            # Check current_score is number between 0-100
            if not isinstance(plan["current_score"], (int, float)) or not (0 <= plan["current_score"] <= 100):
                issues.append("current_score must be number between 0-100")

            # Check suggested_scale is non-empty string
            if not isinstance(plan["suggested_scale"], str) or not plan["suggested_scale"].strip():
                issues.append("suggested_scale must be non-empty string")

            # Check suggested_scale_type is non-empty string
            if not isinstance(plan["suggested_scale_type"], str) or not plan["suggested_scale_type"].strip():
                issues.append("suggested_scale_type must be non-empty string")

            # Check session_target is non-empty string
            if not isinstance(plan["session_target"], str) or not plan["session_target"].strip():
                issues.append("session_target must be non-empty string")

            # Check exercises is non-empty list of strings
            if not isinstance(plan["exercises"], list) or len(plan["exercises"]) == 0:
                issues.append("exercises must be non-empty list")
            elif not all(isinstance(ex, str) and ex.strip() for ex in plan["exercises"]):
                issues.append("all exercises must be non-empty strings")

            if issues:
                return score_result.ScoreResult(
                    name=self.name,
                    value=0.5,
                    reason=f"Validation issues: {'; '.join(issues)}"
                )

            # All checks passed
            return score_result.ScoreResult(
                name=self.name,
                value=1.0,
                reason=f"Valid practice plan with {len(plan['exercises'])} exercises focusing on {plan['focus_area']}"
            )

        except json.JSONDecodeError as e:
            return score_result.ScoreResult(
                name=self.name,
                value=0.1,
                reason=f"Invalid JSON format: {str(e)}"
            )
        except Exception as e:
            return score_result.ScoreResult(
                name=self.name,
                value=0.0,
                reason=f"Error evaluating practice plan: {str(e)}"
            )
