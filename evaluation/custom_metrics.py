"""
Custom Evaluation Metrics for FretCoach

Domain-specific metrics for evaluating AI-generated coaching feedback
and practice recommendations using LLM-as-Judge and heuristic approaches.
"""

import json
from typing import Dict, Any, Optional
from opik.evaluation.metrics import base_metric, score_result


class CoachingHelpfulness(base_metric.BaseMetric):
    """
    Evaluates if coaching feedback is helpful for guitar learners.

    Uses LLM-as-Judge to assess:
    1. Correct identification of the weakest area
    2. Actionability of the advice
    3. Encouraging and supportive tone
    4. Appropriateness for the skill level

    Score: 0.0 to 1.0
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__(
            name="coaching_helpfulness",
            track=True
        )
        self.model = model

    def score(
        self,
        input: Dict[str, Any],
        output: str,
        **kwargs
    ) -> score_result.ScoreResult:
        """Score coaching feedback helpfulness"""

        # Extract context from input
        metrics = input.get("metrics", {})
        weakest_area = input.get("weakest_area", "unknown")
        skill_level = input.get("skill_level", "beginner")
        feedback = output

        # LLM-as-Judge prompt
        judge_prompt = f"""You are evaluating coaching feedback for a guitar learning app.

Context:
- Student skill level: {skill_level}
- Student metrics:
  - Pitch accuracy: {metrics.get('pitch', 0):.0%}
  - Scale conformity: {metrics.get('scale', 0):.0%}
  - Timing stability: {metrics.get('timing', 0):.0%}
- Weakest area: {weakest_area}
- Coaching feedback: "{feedback}"

Evaluate the feedback on these criteria:
1. Does it correctly identify the weakest area?
2. Does it provide specific, actionable advice?
3. Is the tone encouraging and supportive?
4. Is the advice appropriate for the skill level?

Respond with a JSON object:
{{
    "score": <float between 0.0 and 1.0>,
    "reason": "<brief explanation>",
    "identified_weakness_correctly": <true/false>,
    "is_actionable": <true/false>,
    "is_encouraging": <true/false>,
    "appropriate_for_level": <true/false>
}}
"""

        # Call LLM judge (simplified - in production use actual LLM call)
        try:
            from openai import OpenAI
            client = OpenAI()

            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": judge_prompt}],
                response_format={"type": "json_object"},
                temperature=0
            )

            result = json.loads(response.choices[0].message.content)

            return score_result.ScoreResult(name=self.name, 
                value=result["score"],
                reason=result["reason"],
                metadata={
                    "identified_weakness_correctly": result["identified_weakness_correctly"],
                    "is_actionable": result["is_actionable"],
                    "is_encouraging": result["is_encouraging"],
                    "appropriate_for_level": result["appropriate_for_level"]
                }
            )
        except Exception as e:
            # Fallback to heuristic scoring if LLM call fails
            return self._heuristic_score(feedback, weakest_area, skill_level)

    def _heuristic_score(
        self,
        feedback: str,
        weakest_area: str,
        skill_level: str
    ) -> score_result.ScoreResult:
        """Fallback heuristic scoring"""
        score = 0.5  # Baseline
        reasons = []

        feedback_lower = feedback.lower()

        # Check for actionable advice
        action_words = ["try", "practice", "focus", "use", "work on", "keep", "remember"]
        if any(word in feedback_lower for word in action_words):
            score += 0.15
            reasons.append("Contains actionable advice")

        # Check for encouraging tone
        encouraging_words = ["great", "good", "well", "nice", "keep", "excellent"]
        if any(word in feedback_lower for word in encouraging_words):
            score += 0.15
            reasons.append("Encouraging tone detected")

        # Check for specific technique mention
        technique_words = ["metronome", "finger", "fret", "pressure", "position", "scale"]
        if any(word in feedback_lower for word in technique_words):
            score += 0.1
            reasons.append("Specific technique mentioned")

        # Check for weakness identification
        if weakest_area.lower().replace(" ", "_") in feedback_lower:
            score += 0.1
            reasons.append("Addresses weakest area")

        score = min(1.0, max(0.0, score))

        return score_result.ScoreResult(name=self.name, 
            value=score,
            reason=f"Heuristic: {'; '.join(reasons) if reasons else 'Baseline score'}",
            metadata={"heuristic_fallback": True}
        )


class RecommendationAccuracy(base_metric.BaseMetric):
    """
    Measures if following a recommendation led to improvement.

    Compares pre-recommendation avg vs post-recommendation performance
    in the focus area specified by the recommendation.

    Score: 0.0 to 1.0
    - 0.5 = no change
    - 1.0 = 20%+ improvement
    - 0.0 = 20%+ decline
    """

    def __init__(self):
        super().__init__(
            name="recommendation_accuracy",
            track=True
        )

    def score(
        self,
        input: Dict[str, Any],
        output: Dict[str, Any],
        **kwargs
    ) -> score_result.ScoreResult:
        """Calculate improvement after following recommendation"""

        # Extract data
        previous_avg = input.get("user_history", {})
        execution_metrics = output.get("execution_metrics", {})
        focus_area = input.get("recommended_focus", "pitch")

        # Calculate improvement in focus area
        previous_value = previous_avg.get(f"{focus_area}_accuracy", 0)
        current_value = execution_metrics.get(f"{focus_area}_accuracy", 0)

        if previous_value == 0:
            return score_result.ScoreResult(name=self.name, 
                value=0.5,
                reason="No baseline data for comparison",
                metadata={"previous_value": 0, "current_value": current_value}
            )

        improvement = current_value - previous_value
        improvement_pct = improvement / previous_value

        # Score: 0.5 baseline, +/- 0.5 based on improvement
        # +20% improvement = 1.0, -20% = 0.0
        score = 0.5 + (improvement_pct * 2.5)
        score = max(0.0, min(1.0, score))

        return score_result.ScoreResult(name=self.name, 
            value=score,
            reason=f"{'Improved' if improvement > 0 else 'Declined'} by {abs(improvement_pct):.1%} in {focus_area}",
            metadata={
                "previous_value": round(previous_value, 3),
                "current_value": round(current_value, 3),
                "improvement": round(improvement, 3),
                "improvement_percentage": round(improvement_pct, 3),
                "focus_area": focus_area
            }
        )


class PracticePlanCompletionRate(base_metric.BaseMetric):
    """
    Measures if practice plans are actually executed within reasonable time.

    Score: 1.0 if executed, 0.0 if not
    """

    def __init__(self, time_window_hours: int = 48):
        super().__init__(
            name="practice_plan_completion_rate",
            track=True
        )
        self.time_window_hours = time_window_hours

    def score(
        self,
        input: Dict[str, Any],
        output: Dict[str, Any],
        expected_output: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> score_result.ScoreResult:
        """Check if plan was completed"""

        executed = expected_output.get("completion", False) if expected_output else False
        hours_since_generation = input.get("hours_since_generation", 0)

        if not executed and hours_since_generation < self.time_window_hours:
            return score_result.ScoreResult(name=self.name, 
                value=0.5,
                reason=f"Plan not yet executed ({hours_since_generation:.1f}h since generation)",
                metadata={"status": "pending", "hours_elapsed": hours_since_generation}
            )

        if executed:
            return score_result.ScoreResult(name=self.name, 
                value=1.0,
                reason="Practice plan was executed",
                metadata={"status": "completed"}
            )

        return score_result.ScoreResult(name=self.name, 
            value=0.0,
            reason=f"Plan not executed within {self.time_window_hours}h window",
            metadata={"status": "expired", "hours_elapsed": hours_since_generation}
        )


class LearningProgressRate(base_metric.BaseMetric):
    """
    Measures user improvement velocity over time.

    Calculates week-over-week improvement in overall performance
    across all tracked metrics.

    Score: 0.0 to 1.0
    - 0.5 = no change
    - 1.0 = significant improvement
    - 0.0 = significant decline
    """

    def __init__(self):
        super().__init__(
            name="learning_progress_rate",
            track=True
        )

    def score(
        self,
        input: Dict[str, Any],
        output: Dict[str, Any],
        **kwargs
    ) -> score_result.ScoreResult:
        """Calculate learning velocity"""

        # Expects time-series data in input
        sessions = input.get("sessions", [])

        if len(sessions) < 2:
            return score_result.ScoreResult(name=self.name, 
                value=0.5,
                reason="Insufficient data (need at least 2 sessions)",
                metadata={"sessions_analyzed": len(sessions)}
            )

        # Calculate average performance for each session
        def avg_performance(session):
            return (
                session.get('pitch_accuracy', 0) +
                session.get('scale_conformity', 0) +
                session.get('timing_stability', 0)
            ) / 3

        # Split into first half and second half
        mid = len(sessions) // 2
        first_half = sessions[:mid]
        second_half = sessions[mid:]

        # Calculate average performance for each half
        first_avg = sum(avg_performance(s) for s in first_half) / len(first_half)
        second_avg = sum(avg_performance(s) for s in second_half) / len(second_half)

        improvement = second_avg - first_avg

        # Score: 0.5 baseline, +0.5 for 10% improvement, -0.5 for 10% decline
        score = 0.5 + (improvement * 5)
        score = max(0.0, min(1.0, score))

        return score_result.ScoreResult(name=self.name, 
            value=score,
            reason=f"Performance {'improved' if improvement > 0 else 'declined'} by {abs(improvement):.1%}",
            metadata={
                "first_half_avg": round(first_avg, 3),
                "second_half_avg": round(second_avg, 3),
                "improvement": round(improvement, 3),
                "sessions_analyzed": len(sessions)
            }
        )


class ResponseRelevance(base_metric.BaseMetric):
    """
    Checks if the AI response is relevant to the user context.

    Uses built-in Opik answer relevance template or custom evaluation.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__(
            name="response_relevance",
            track=True
        )
        self.model = model

    def score(
        self,
        input: Dict[str, Any],
        output: str,
        **kwargs
    ) -> score_result.ScoreResult:
        """Check response relevance to input"""

        # Build context string
        context = f"Scale: {input.get('scale_name', 'unknown')}\n"
        context += f"Weakest area: {input.get('weakest_area', 'unknown')}\n"
        context += f"Skill level: {input.get('skill_level', 'unknown')}\n"

        relevance_prompt = f"""You are evaluating if an AI response is relevant to the given context.

Context:
{context}

AI Response:
"{output}"

Is the response relevant to the context? Consider:
1. Does it address the weakest area?
2. Is it appropriate for the skill level?
3. Does it mention the correct scale or technique?

Respond with JSON:
{{
    "relevant": <true/false>,
    "score": <float 0.0-1.0>,
    "reason": "<brief explanation>"
}}
"""

        try:
            from openai import OpenAI
            client = OpenAI()

            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": relevance_prompt}],
                response_format={"type": "json_object"},
                temperature=0
            )

            result = json.loads(response.choices[0].message.content)

            return score_result.ScoreResult(name=self.name, 
                value=result["score"],
                reason=result["reason"],
                metadata={"relevant": result["relevant"]}
            )
        except Exception:
            # Fallback
            return score_result.ScoreResult(name=self.name, 
                value=0.7,
                reason="Could not evaluate relevance",
                metadata={"fallback": True}
            )


class SafetyModeration(base_metric.BaseMetric):
    """
    Safety check for coaching feedback using OpenAI moderation API.
    """

    def __init__(self):
        super().__init__(
            name="safety_moderation",
            track=True
        )

    def score(
        self,
        input: Dict[str, Any],
        output: str,
        **kwargs
    ) -> score_result.ScoreResult:
        """Check for safety issues in response"""

        try:
            from openai import OpenAI
            client = OpenAI()

            response = client.moderations.create(input=output)

            if response.results[0].flagged:
                return score_result.ScoreResult(name=self.name, 
                    value=0.0,
                    reason="Content flagged by moderation API",
                    metadata={"flagged": True, "categories": response.results[0].categories.model_dump()}
                )

            return score_result.ScoreResult(name=self.name, 
                value=1.0,
                reason="Content passed safety checks",
                metadata={"flagged": False}
            )
        except Exception:
            return score_result.ScoreResult(name=self.name, 
                value=0.5,
                reason="Could not perform safety check",
                metadata={"error": True}
            )
