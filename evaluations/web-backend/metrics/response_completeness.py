"""
Custom metric to evaluate response completeness and helpfulness.
"""
from opik.evaluation.metrics import base_metric, score_result


class ResponseCompleteness(base_metric.BaseMetric):
    """
    Evaluates if the agent's response is complete and helpful.

    Checks for:
    - Non-empty response
    - Appropriate length
    - No error messages
    - Actionable content
    """

    def __init__(self, name: str = "response_completeness"):
        super().__init__(name=name)
        self.name = name

    def score(self, input: str, output: str, is_ai_greeting: bool = False, **_kwargs):
        """
        Score the response completeness.

        Args:
            input: The user's query/input
            output: The agent's response text
            is_ai_greeting: Whether the input is an AI greeting (skip scoring if True)

        Returns:
            ScoreResult with value 0-1 and explanation, or None if should skip
        """
        # Skip scoring for AI greetings (not real user queries)
        if is_ai_greeting:
            return None

        try:
            if not output or not output.strip():
                return score_result.ScoreResult(
                    name=self.name,
                    value=0.0,
                    reason="Empty response"
                )

            response_lower = output.lower()
            response_length = len(output)

            # Check for error indicators
            error_indicators = [
                "error occurred",
                "i apologize",
                "encountered an issue",
                "something went wrong",
                "failed to",
                "unable to"
            ]

            has_error = any(indicator in response_lower for indicator in error_indicators)
            if has_error:
                return score_result.ScoreResult(
                    name=self.name,
                    value=0.2,
                    reason="Response contains error indicators"
                )

            # Check if response is too short (likely incomplete)
            if response_length < 50:
                return score_result.ScoreResult(
                    name=self.name,
                    value=0.4,
                    reason=f"Response too short ({response_length} chars)"
                )

            # Check for actionable content indicators
            actionable_indicators = [
                "practice",
                "focus",
                "improve",
                "try",
                "work on",
                "exercise",
                "session",
                "scale",
                "accuracy",
                "timing"
            ]

            has_actionable = any(indicator in response_lower for indicator in actionable_indicators)

            if has_actionable and response_length >= 100:
                return score_result.ScoreResult(
                    name=self.name,
                    value=1.0,
                    reason=f"Complete and actionable response ({response_length} chars)"
                )
            elif has_actionable:
                return score_result.ScoreResult(
                    name=self.name,
                    value=0.8,
                    reason=f"Actionable but could be more detailed ({response_length} chars)"
                )
            elif response_length >= 100:
                return score_result.ScoreResult(
                    name=self.name,
                    value=0.7,
                    reason="Response is detailed but lacks clear action items"
                )
            else:
                return score_result.ScoreResult(
                    name=self.name,
                    value=0.6,
                    reason="Response could be more complete and actionable"
                )

        except Exception as e:
            return score_result.ScoreResult(
                name=self.name,
                value=0.0,
                reason=f"Error evaluating response: {str(e)}"
            )
