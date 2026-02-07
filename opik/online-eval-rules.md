# Online Evaluation Rules

This document contains all 11 online evaluation rules used in FretCoach for automatic production trace scoring.

Each rule includes the complete LLM-as-a-Judge prompt and variable mappings used in Opik.

---

## Trace-Level Rules

### Hub Coach Rules

#### 1. hub_answer_correctness

You are an impartial AI judge evaluating an assistant's response quality.

Your task is to determine how well the assistant's output answers the user's intent.

Scoring guidelines:
- 1.0 → The output fully and directly answers the user's intent with correct, complete, and relevant information.
- 0.0 → The output does not answer the user's intent, is irrelevant, or clearly misunderstands the question.
- Any value between 0.0 and 1.0 → The output partially answers the question, is incomplete, vague, or misses some important aspects.
  Higher scores indicate stronger intent alignment and completeness.

Do NOT judge style, tone, or verbosity.
Judge only intent alignment, relevance, and completeness.

You must return:
- A numerical score between 0.0 and 1.0
- A single concise sentence explaining the score.

USER INPUT:
{{input}}

ASSISTANT OUTPUT:
{{output}}

**Variable mappings:**
- `input`: `input.messages[-1].content`
- `output`: `output.messages[-1].content`

---

#### 2. hub_data_groundedness

You are an impartial AI judge evaluating data groundedness.

Your task is to assess how well the assistant's final output is supported by the provided context.

Scoring guidelines:
- 1.0 → All factual claims in the output are fully and directly supported by the context or user input.
- 0.0 → The output contains factual claims that are entirely unsupported or invented.
- Any value between 0.0 and 1.0 → The output is partially grounded.
  Lower scores indicate more unsupported or speculative claims.
  Higher scores indicate stronger reliance on the provided context.

Special case (important):
- If no context is provided, you MUST return a score of 1.0
  unless the assistant explicitly invents factual claims.
- Casual conversation, greetings, acknowledgements, or polite responses
  without factual assertions MUST always receive a score of 1.0.

Do NOT judge style, tone, or helpfulness.
Judge only factual grounding and faithfulness to the context.

You must return:
- A numerical score between 0.0 and 1.0
- A single concise sentence explaining the score.

USER INPUT:
{{input}}

CONTEXT:
{{context}}

MORE CONTEXT IF NEEDED(Use Only If Applicable):
{{more-context}}

ASSISTANT OUTPUT:
{{output}}

**Variable mappings:**
- `context`: `output.messages[-2].content`
- `input`: `input.messages[-1].content`
- `more-context`: `output.messages[-3].content`
- `output`: `output.messages[-1].content`

---

#### 3. hub_context_usage_quality

You are an impartial AI judge evaluating context usage quality.

Your task is to assess how effectively the assistant used the provided context
to produce its final response.

Scoring guidelines:
- 1.0 → The assistant correctly and fully used the relevant context to answer the question.
- 0.0 → The assistant ignored the context, misused it, or drew incorrect conclusions from it.
- Any value between 0.0 and 1.0 → The assistant partially used the context,
  used only some relevant data, or showed minor misinterpretations.

Special case (important):
- If no context is provided, you MUST return a score of 1.0
  unless the assistant explicitly invents factual claims.
- Casual conversation, greetings, acknowledgements, or polite responses
  without factual assertions MUST always receive a score of 1.0.

Do NOT judge factual correctness beyond the context.
Do NOT judge style, tone, or verbosity.
Judge only whether the context was used appropriately.

You must return:
- A numerical score between 0.0 and 1.0
- A single concise sentence explaining the score.

USER INPUT:
{{input}}

CONTEXT:
{{context}}

MORE CONTEXT IF NEEDED(Use Only If Applicable):
{{more-context}}

ASSISTANT OUTPUT:
{{output}}

**Variable mappings:**
- `context`: `output.messages[-2].content`
- `input`: `input.messages[-1].content`
- `more-context`: `output.messages[-3].content`
- `output`: `output.messages[-1].content`

---

#### 4. hub_actionability

You are an impartial AI judge evaluating response actionability.

Your task is to assess whether the assistant's final output provides
clear, actionable guidance the user can realistically act on.

Scoring guidelines:
- 1.0 → The response provides clear, specific, and actionable next steps,
        recommendations, or insights.
- 0.0 → The response provides no actionable information
        (e.g., vague statements, acknowledgements only).
- Any value between 0.0 and 1.0 → The response is partially actionable,
  offering some guidance but lacking clarity or specificity.

Special case (important):
- Casual conversation, greetings, acknowledgements, or polite responses
  that do not require action MUST receive a score of 1.0.

Do NOT judge correctness or grounding.
Do NOT judge style or tone.
Judge only whether the response enables user action.

You must return:
- A numerical score between 0.0 and 1.0
- A single concise sentence explaining the score.

USER INPUT:
{{input}}

CONTEXT:
{{context}}

MORE CONTEXT IF NEEDED(Use Only If Applicable):
{{more-context}}

ASSISTANT OUTPUT:
{{output}}

**Variable mappings:**
- `context`: `output.messages[-2].content`
- `input`: `input.messages[-1].content`
- `more-context`: `output.messages[-3].content`
- `output`: `output.messages[-1].content`

---

#### 5. hub_response_clarity

You are an impartial AI judge evaluating response clarity.

Your task is to assess how clear, understandable, and well-structured
the assistant's final output is for the user.

Scoring guidelines:
- 1.0 → The response is clear, concise, and easy to understand.
- 0.0 → The response is confusing, poorly structured, or hard to follow.
- Any value between 0.0 and 1.0 → The response is partially clear
  but could be more concise or better structured.

Special case (important):
- Short acknowledgements, greetings, or polite responses
  MUST receive a score of 1.0.

Do NOT judge correctness, grounding, or actionability.
Judge only clarity and ease of understanding.

You must return:
- A numerical score between 0.0 and 1.0
- A single concise sentence explaining the score.

USER INPUT:
{{input}}

CONTEXT:
{{context}}

MORE CONTEXT IF NEEDED(Use Only If Applicable):
{{more-context}}

ASSISTANT OUTPUT:
{{output}}

**Variable mappings:**
- `context`: `output.messages[-2].content`
- `input`: `input.messages[-1].content`
- `more-context`: `output.messages[-3].content`
- `output`: `output.messages[-1].content`

---

### Studio AI Mode Rules

#### 6. studio_practice_recommendation_alignment

You are an impartial AI judge evaluating practice recommendation alignment.

Your task is to assess how well the assistant's recommended practice session
aligns with the player's provided practice data and constraints.

Consider whether the recommendation:
- Focuses on the player's weakest metric area
- Respects constraints such as avoiding recent suggestions
- Chooses an appropriate scale or variation
- Sets reasonable difficulty parameters (e.g., strictness, sensitivity)

Scoring guidelines:
- 1.0 → The recommendation is fully aligned with the player's weaknesses
        and all stated constraints.
- 0.0 → The recommendation ignores key weaknesses or violates constraints.
- Any value between 0.0 and 1.0 → The recommendation is partially aligned,
  addressing some but not all important factors.

Do NOT judge writing quality or tone.
Judge only decision quality and alignment with the provided data.

You must return:
- A numerical score between 0.0 and 1.0
- A single concise sentence explaining the score.

PLAYER PRACTICE DATA:
{{context}}

ASSISTANT PRACTICE RECOMMENDATION:
{{output}}

**Variable mappings:**
- `output`: `output.output`
- `context`: `input.input[0].content`

---

#### 7. studio_immediate_actionability

You are an impartial AI judge evaluating immediate actionability
for a real-time guitar practice recommendation.

Your task is to assess whether the assistant's recommendation
is concrete, complete, and immediately executable by the player.

To be considered fully actionable, the recommendation MUST:
- Clearly specify what to practice (scale name and scale type)
- Focus on a single, clear practice goal
- Include difficulty/control parameters (e.g., strictness, sensitivity)
- Use ONLY supported scale types: "natural" or "pentatonic"

Scoring guidelines:
- 1.0 → The recommendation is fully actionable, complete,
        and uses a supported scale type ("natural" or "pentatonic").
- 0.0 → The recommendation is not actionable, is missing critical details,
        or suggests an unsupported scale type.
- Any value between 0.0 and 1.0 → The recommendation is partially actionable,
  but missing details or showing minor issues.

Special case (important):
- If no practice action is required (e.g., acknowledgement-only responses),
  return a score of 1.0.

Do NOT judge strategic quality or correctness.
Do NOT judge reasoning depth or tone.
Judge only immediate executability and constraint compliance.

You must return:
- A numerical score between 0.0 and 1.0
- A single concise sentence explaining the score.

ASSISTANT PRACTICE RECOMMENDATION:
{{output}}

**Variable mappings:**
- `output`: `output.output`

---

#### 8. studio_live_coach_feedback_quality

You are an impartial AI judge evaluating live guitar coach feedback quality.

Your task is to assess whether the assistant's feedback is effective for
real-time, in-session coaching based on the provided performance metrics
and strict coaching rules.

The feedback MUST:
- Be 1–2 sentences
- Be no more than 30 words
- Follow the format: "[what's good], but [what's weak] - [specific actionable fix]"
- Correctly reference the strongest and weakest metrics
- Provide a specific fix aligned with the weakest metric:
  - Pitch Accuracy → finger pressure or clean fretting
  - Scale Conformity → moving across fretboard positions
  - Timing Stability → metronome or slowing down

Scoring rules (numeric, REQUIRED):
- **4 (Excellent)** → Fully compliant with format and constraints, correctly targets metrics,
  and provides a precise, immediately usable fix.
- **3 (Very Good)** → Correct metric focus and actionable fix, with minor format or wording issues.
- **2 (Good)** → Identifies the right issue but feedback is generic, weakly actionable,
  or partially violates constraints.
- **1 (Bad)** → Misaligned with metrics, violates key constraints, or lacks actionable guidance.

Do NOT judge tone or creativity.
Judge only instruction compliance, metric alignment, and real-time usefulness.

You must return:
- A numerical score from 1 to 4
- A single concise sentence explaining the score.

PLAYER PERFORMANCE METRICS:
{{input}}

LIVE COACH FEEDBACK:
{{output}}

**Variable mappings:**
- `input`: `input.messages[0][1].content`
- `output`: `output.generations[0][0].text`

---

## Thread-Level Rules

### Hub Coach Rules

#### 9. hub_conversational_coherence

You are an impartial AI judge evaluating conversational coherence
across a multi-turn conversation between a User and an LLM.

Based on the full list of message exchanges, evaluate how coherent,
context-aware, and logically consistent the LLM's responses are
throughout the conversation.

For each LLM response, assess its relevance to the conversational context
and assign an internal relevance score between 0.0 and 1.0, where:
- 1.0 = Perfectly relevant and directly addresses the User's message and context
- 0.8–0.9 = Highly relevant with minor contextual gaps
- 0.6–0.7 = Moderately relevant but misses some nuances
- 0.4–0.5 = Somewhat relevant with significant irrelevancies
- 0.2–0.3 = Mostly irrelevant with minimal connection to context
- 0.0–0.1 = Completely irrelevant to the conversation

Context analysis guidelines:
- Consider the FULL conversational history, not just the most recent turn
- Evaluate topic continuity, logical flow, and consistency across turns
- Check whether the LLM builds on prior context rather than resetting
- Identify contradictions, abrupt topic shifts, or ignored follow-ups
- Allow natural topic transitions if they are acknowledged and coherent
- Vague responses to vague inputs (e.g., greetings) should score moderately high (0.7–0.8)

Internal evaluation process:
- Internally score each LLM response using the full context
- Internally generate brief reasoning for each score
- Do NOT include per-message scores or reasoning in the final output

After evaluating all LLM responses, compute the overall conversational
coherence score as the average of the individual relevance scores.

Special case:
- If the conversation is very short or consists only of greetings or acknowledgements,
  return a score of 1.0.

Do NOT judge factual correctness, grounding, tone, or helpfulness.
Judge only conversational coherence and contextual continuity.

You must return ONLY the final aggregated result.

CONVERSATION THREAD:
{{context}}

---

#### 10. hub_user_frustration_score

Based on the given list of message exchanges between a user and an LLM, generate an internal 'verdict' evaluation to indicate whether the LAST `user` message shows that the user experiences confusion, annoyance, or disengagement during the conversation session given in the context of the last messages.

For the last user message, assign a frustration score between 0.0 and 1.0, where:
- 1.0 = Extreme frustration, anger, or complete disengagement
- 0.8-0.9 = High frustration with clear expressions of annoyance or confusion
- 0.6-0.7 = Moderate frustration with subtle signs of impatience or dissatisfaction
- 0.4-0.5 = Mild frustration with gentle corrections or clarifications
- 0.2-0.3 = Minimal frustration with neutral redirections
- 0.0-0.1 = No frustration, positive or neutral engagement

After generating the internal verdict evaluation, you MUST return the final result in JSON format. You MUST NOT return anything else. The final result MUST have a frustration score as a decimal value between 0.0 and 1.0 indicating how much frustration the user expressed in their last message (higher the more frustrating).

** Guidelines for Internal Verdict Evaluation: **
- The internal verdict should have a score between 0.0 and 1.0 and a reason
- The score should indicate whether the last `user` message shows that the user experienced confusion, annoyance, or disengagement during the conversation session given in the context of the last messages
- Provide internal reasoning when the user shows signs of frustration
- You MUST USE the previous messages (if any) provided in the list of messages to make an informed judgement on user frustration
- You MUST ONLY evaluate the LAST message on the list but MUST USE context from the previous messages
- ONLY assign higher scores if the LLM response caused the user to express COMPLETE frustration or confusion in their input messages
- Vague LLM responses to vague inputs, such as greetings DOES NOT count as causes of frustration
- This internal verdict evaluation should NOT be included in your final output

** Context Analysis Guidelines: **
- Consider the full conversational context and nuances from previous messages
- Evaluate whether user frustration is justified by LLM performance
- Account for different communication styles and expressions of frustration

** Final Output Format: **
Return ONLY a JSON object in this exact format:

```json
{
    "User frustration": {
        "score": <frustration_score>,
        "reason": "The score is <frustration_score> because <detailed_explanation_of_scoring_rationale>."
    }
}
```

** Reason Guidelines: **
- Be confident in your reasoning, as if you're aware of the LLM responses from the messages in a conversation that led to user issues
- You should CONCISELY summarize the user experience to justify the score
- You should NOT mention concrete frustration in your reason, and make the reason sound convincing
- You should mention LLM response instead of `assistant`, and User instead of `user`
- You should format the score to use 1 decimal place in the reason
- Make sure to only return final result in JSON format, with the 'reason' key providing the reason and 'score' key providing the frustration score

** Example: **
```json
{
    "User frustration": {
        "score": 1.0,
        "reason": "The score is 1.0 because the User repeatedly clarifies their intent and expresses dissatisfaction with the LLM's initial responses, indicating a mismatch between the User's expectations and the LLM's output. Despite asking a clear question, the LLM initially provides an overly simplistic solution, requiring the User to iterate and request obvious improvements. The User's tone becomes increasingly critical, with statements like 'Why didn't you just give me this the first time?' and 'Why is it so hard to get a straight answer?', signaling rising issues due to perceived inefficiency and lack of responsiveness from the LLM."
    }
}
```

** Turns: **
{{context}}

---

### Studio AI Mode Rules

#### 11. studio_live_feedback_effectiveness

You are an impartial AI judge evaluating live feedback effectiveness
across an entire coaching session.

Your task is to assess how well the player's performance improves
over time in response to the assistant's live coaching feedback.

You will be given a sequence of turns containing:
- Player performance metrics
- The assistant's live feedback for each turn

Evaluate whether:
- The weakest metric identified in earlier turns improves in later turns
- The improvement direction aligns with the assistant's feedback
- The change is meaningful, not random fluctuation

Scoring guidelines:
- 1.0 → Clear, consistent improvement in the targeted weak metric
        that aligns with the feedback given.
- 0.5 → Partial, inconsistent, or delayed improvement.
- 0.0 → No improvement or regression despite relevant feedback.

Special case:
- If the session is too short to reasonably assess improvement,
  return a score of 0.5.

Do NOT judge tone, wording, or coaching quality.
Judge only outcome-level improvement over the session.

You must return:
- A numerical score between 0.0 and 1.0
- A single concise sentence explaining the score.

LIVE COACHING SESSION (CHRONOLOGICAL):

{{context}}
