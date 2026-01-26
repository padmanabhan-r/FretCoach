"""
LLM Utilities for Cost Tracking and Token Counting

Provides utilities for tracking token usage and calculating costs
for various LLM providers used in FretCoach.
"""
import tiktoken
from typing import Dict, Optional


# Pricing per 1K tokens (as of Jan 2026)
# FretCoach uses only these two models for text generation
MODEL_PRICING = {
    # OpenAI - used for desktop backend (coaching, recommendations)
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},

    # Google Gemini - used for web backend (chat)
    "gemini-2.5-flash": {"input": 0.0, "output": 0.0},  # Free tier

    # Note: TTS uses same pricing as base gpt-4o-mini
    "gpt-4o-mini-tts": {"input": 0.00015, "output": 0.0006},
}


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Count tokens in text for given model.

    Args:
        text: The text to count tokens for
        model: The model name (defaults to gpt-4o-mini)

    Returns:
        Number of tokens
    """
    if not text:
        return 0

    try:
        # For OpenAI models, use tiktoken
        if model.startswith("gpt"):
            # Handle TTS models
            base_model = model.replace("-tts", "")
            encoding = tiktoken.encoding_for_model(base_model)
            return len(encoding.encode(text))
        # For other models, approximate
        else:
            # Rough approximation: 1 token ≈ 4 characters
            return len(text) // 4
    except Exception as e:
        # Fallback approximation if tiktoken fails
        return len(text) // 4


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int
) -> float:
    """
    Calculate cost in USD for LLM call.

    Args:
        model: The model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Cost in USD
    """
    if model not in MODEL_PRICING:
        # Unknown model, return 0
        return 0.0

    pricing = MODEL_PRICING[model]
    cost = (
        (input_tokens / 1000 * pricing["input"]) +
        (output_tokens / 1000 * pricing["output"])
    )
    return round(cost, 6)  # Round to 6 decimal places


def track_llm_call(
    prompt: str,
    response: str,
    model: str = "gpt-4o-mini",
    additional_metadata: Optional[Dict] = None
) -> Dict:
    """
    Track LLM call and return comprehensive metadata.

    Args:
        prompt: The input prompt
        response: The LLM response
        model: The model used
        additional_metadata: Any additional metadata to include

    Returns:
        Dictionary with token counts, costs, and metadata
    """
    input_tokens = count_tokens(prompt, model)
    output_tokens = count_tokens(response, model)
    total_tokens = input_tokens + output_tokens
    cost = calculate_cost(model, input_tokens, output_tokens)

    metadata = {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "total_cost": cost,
        "cost_currency": "USD"
    }

    # Add any additional metadata
    if additional_metadata:
        metadata.update(additional_metadata)

    return metadata


def estimate_prompt_cost(prompt: str, model: str = "gpt-4o-mini", expected_output_tokens: int = 100) -> float:
    """
    Estimate the cost of a prompt before calling the LLM.

    Args:
        prompt: The input prompt
        model: The model to use
        expected_output_tokens: Expected number of output tokens

    Returns:
        Estimated cost in USD
    """
    input_tokens = count_tokens(prompt, model)
    return calculate_cost(model, input_tokens, expected_output_tokens)


def format_cost(cost: float) -> str:
    """
    Format cost for display.

    Args:
        cost: Cost in USD

    Returns:
        Formatted string (e.g., "$0.0012" or "$0.12")
    """
    if cost < 0.01:
        return f"${cost:.4f}"
    else:
        return f"${cost:.2f}"
