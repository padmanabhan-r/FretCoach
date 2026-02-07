# Opik Integration in FretCoach

## Features Implemented

### 1. Traces with Metadata and Tags

All LLM calls are logged as traces in Opik with structured tags for filtering and organization.

**Hub Coach Chats:**
- Tags: `ai-coach-chat`, `fretcoach-hub`, `from-hub-dashboard`, `gemini-2.5-flash`, `practice-plan`
- Tracks AI coach conversations in the web dashboard

<p align="center">
  <img src="images/hub-traces.png" width="700">
  <br>
  <em>Hub coach chat traces with proper tags in Opik dashboard</em>
</p>

**AI Mode (Practice Recommendations):**
- Tags: `fretcoach-core`, `gpt-4o-mini`, `ai-mode`, `fretcoach-studio`, `practice-recommendation`
- Tracks personalized practice recommendations

<p align="center">
  <img src="images/ai-mode-traces.png" width="700">
  <br>
  <em>AI mode practice recommendation traces</em>
</p>

**Live AI Feedback in Session:**
- Tags: `fretcoach-core`, `gpt-4o-mini`, `ai-mode`, `fretcoach-studio`, `live-feedback`
- Tracks real-time coaching feedback during practice

<p align="center">
  <img src="images/live-feedback-traces.png" width="700">
  <br>
  <em>Live AI feedback traces during practice sessions</em>
</p>

---

### 2. Thread Management

Structured `thread_id` to group related LLM calls and maintain conversation context.

**Thread Naming Conventions:**
- **Hub Coach:** `hub-{user_id}` - Groups all coach chat messages for a user
- **AI Mode:** `{deployment}-ai-mode-{practice_id}` - Maintains thread across recommendations
- **Live Feedback:** `{session_id}-live-aicoach-feedback` - Groups feedback within a practice session

<p align="center">
  <img src="images/thread-management.png" width="700">
  <br>
  <em>Thread IDs grouping related traces in Opik</em>
</p>

---

### 3. Agent Graph Visualization

LangGraph execution flows visualized in Opik using `workflow.get_graph(xray=True)`.

Shows complete agent reasoning path: agent → tool calls (`execute_sql_query`, `get_database_schema`) → decision nodes → response.

<p align="center">
  <img src="images/agent-graph.png" width="700">
  <br>
  <em>LangGraph agent execution flow in Opik</em>
</p>

---

### 4. Annotation Queues

Used annotation queues for human-in-the-loop evaluation of agent outputs.

**Implementation:**
- Custom feedback definitions for LLM output quality
- Manual review and rating using custom criteria
- Structured feedback collection for agent improvements

<p align="center">
  <img src="images/annotation-queue.png" width="700">
  <br>
  <em>Annotation queue with reviewed LLM outputs</em>
</p>

---

### 5. Datasets and Prompts

Created datasets and prompts for reproducible experiments and evaluations.

**Datasets:**
- Curated test cases from real user sessions
- Used across experiment runs for consistent testing

**Prompts:**
- Version-controlled coaching prompt templates
- Used in playground for rapid iteration

<p align="center">
  <img src="images/datasets.png" width="700">
  <br>
  <em>Datasets created for experiment runs</em>
</p>

<p align="center">
  <img src="images/prompts.png" width="700">
  <br>
  <em>Saved prompts</em>
</p>

---

### 6. Experiments and Custom Metrics

Evaluated LLM performance using both default Opik metrics and custom-created metrics.

**Default Metrics:**
- Opik's built-in evaluation metrics for response quality

**Custom Metrics:**
- Domain-specific metrics tailored to guitar coaching context
- Measures coaching quality and relevance

<p align="center">
  <img src="images/experiments-default.png" width="700">
  <br>
  <em>Experiments with default Opik metrics</em>
</p>

<p align="center">
  <img src="images/experiments-custom.png" width="700">
  <br>
  <em>Experiments with custom metric</em>
</p>

---

### 7. Optimization Studio

Used Optimization Studio to improve the prompt used in the live feedback module.

**Results:**
- **32% increase** in `llm_judge_metric` custom metric
- Improved coaching feedback quality
- Optimized for better real-time guidance

<p align="center">
  <img src="images/optimization-studio.png" width="700">
  <br>
  <em>Optimization Studio results for live feedback prompt</em>
</p>

---

### 8. OpikAssist for Token Usage Optimization

Used OpikAssist to analyze traces and optimize token usage for hub coach chats.

**Problem Identified:**
- Excessive token usage (4,877 tokens) and long duration (7,873 ms)
- Lengthy prompts with redundant context and full SQL data

**Actions Taken:**
- Refined system and user prompts based on OpikAssist suggestions
- Streamlined SQL result formatting to essential data only
- Removed redundant context and consolidated guidelines

**Results:**
- Significant token usage reduction
- Improved response latency
- Better cost-performance ratio

<p align="center">
  <img src="images/opik-assist.png" width="700">
  <br>
  <em>OpikAssist analyzing trace for token usage optimization</em>
</p>

---

### 9. Project-Specific Configurations

Configured custom feedback definitions and AI providers for comprehensive evaluation.

**Feedback Definitions:**
- Custom fields for manual LLM output rating
- Human-in-the-loop feedback on traces
- Categorical ratings: "AI Coach Conversation Rating" and "User Feedback"

**AI Providers:**
- Perplexity's Sonar Pro for automated evaluations
- OpenRouter models for diverse evaluation perspectives
- Enhanced evaluation capabilities beyond default Opik models

<p align="center">
  <img src="images/feedback-definitions.png" width="700">
  <br>
  <em>Custom feedback definitions for manual trace ratings</em>
</p>

<p align="center">
  <img src="images/config-models.png" width="700">
  <br>
  <em>Custom AI providers configured for automated evaluations</em>
</p>
