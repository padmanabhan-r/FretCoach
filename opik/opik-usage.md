# Opik Integration in FretCoach

## Features Implemented

### 1. Traces with Metadata and Tags

All LLM calls are logged as traces in Opik with proper tags to organize and filter different types of interactions.

**Hub Coach Chats:**
- Tags: `ai-coach-chat`,`fretcoach-hub`, `from-hub-dashboard`, `gemini-2.5-flash`, `practice-plan`
- Used for AI coach conversations in the web dashboard

![Hub Coach Chat Traces](images/hub-traces.png)

**AI Mode (Practice Recommendations):**
- Tags: `fretcoach-core`, `gpt-4o-mini`, `ai-mode`, `fretcoach-studio`, `practice-recommendation`
- Used for generating personalized practice recommendations

![AI Mode Traces](images/ai-mode-traces.png)

**Live AI Feedback in Session:**
- Tags: `fretcoach-core`, `gpt-4o-mini`, `ai-mode`, `fretcoach-studio`, `live-feedback`
- Used for real-time coaching feedback during practice sessions

![Live Feedback Traces](images/live-feedback-traces.png)

**Session Summary:**
- Tags: `fretcoach-core`, `gpt-4o-mini`, `ai-mode`, `fretcoach-studio`, `session-summary`
- Used for generating end-of-session summaries

![Session Summary Traces](placeholder-session-summary-traces.png)
