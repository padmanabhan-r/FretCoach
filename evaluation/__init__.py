"""
FretCoach Custom Evaluation Metrics

This package contains domain-specific evaluation metrics for assessing
AI-generated coaching feedback and practice recommendations.
"""

from .custom_metrics import (
    CoachingHelpfulness,
    RecommendationAccuracy,
    PracticePlanCompletionRate,
    LearningProgressRate
)

__all__ = [
    "CoachingHelpfulness",
    "RecommendationAccuracy",
    "PracticePlanCompletionRate",
    "LearningProgressRate"
]
