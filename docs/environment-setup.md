# Environment Setup

Complete environment configuration guide for all FretCoach components.

## Prerequisites

- **Python 3.12+** (required for all backend components)
- **Node.js 18+** and npm (required for frontend applications)
- **PostgreSQL** access (Supabase recommended)

## Quick Start

Each component requires a `.env` file with specific credentials. Follow the sections below to configure your setup.

## Database Configuration (Supabase)

FretCoach uses PostgreSQL hosted on Supabase for session tracking and practice plan storage.

**Required for:** All components (Studio, Hub, Portable)

Create a Supabase project at [supabase.com](https://supabase.com) and add to your `.env`:

```env
DB_HOST=your_supabase_host.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_supabase_password
```

**Testing connection:**
```bash
# From any backend directory
uv run python -c "from backend.core.session_logger import SessionLogger; print('Connected!')"
```

**Note:** Session logging is optional. If database is unavailable, practice sessions continue without persistence.

## AI Services API Keys

FretCoach uses multiple AI providers for coaching and practice plan generation.

**Required for:** AI Practice Mode, Live Coaching, Hub Chat

### OpenAI

Used for GPT-4o-mini-TTS (vocal coaching) and ChatGPT-based coaching.

Get API key: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

```env
OPENAI_API_KEY=sk-proj-...your_key
```

### Google Gemini

Used for Gemini (practice plan generation, Hub chat agent).

Get API key: [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

```env
GOOGLE_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3-flash-preview
```

### Additional AI Providers (Optional)

FretCoach supports multiple AI providers for flexibility:

```env
# Groq (optional - fast inference)
GROQ_API_KEY=your_groq_api_key

# OpenRouter (optional - access to multiple models)
OPENROUTER_API_KEY=your_openrouter_api_key

# Perplexity (optional - for research capabilities)
PPLX_API_KEY=your_perplexity_api_key

# Tavily (optional - for research agents with external search)
TAVILY_API_KEY=your_tavily_api_key

# Anthropic via Minimax (optional)
ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key
```

**Cost:** All providers offer free tiers suitable for personal use. FretCoach's AI calls are lightweight.

## Smart Bulb Setup (Tuya)

Ambient lighting provides real-time visual feedback during practice.

**Required for:** Ambient lighting feature (optional)

**Compatible devices:** Any Tuya-compatible smart bulb (Havells, Wipro, generic Tuya)

**Setup:**

1. Install bulb and connect to Tuya Smart app
2. Create developer account at [iot.tuya.com](https://iot.tuya.com)
3. Create Cloud Project and link your app account
4. Get credentials from Cloud → API Explorer

```env
HAVELLS_ACCESS_ID=your_access_id
HAVELLS_ACCESS_SECRET=your_access_secret
HAVELLS_DEVICE_ID=your_bulb_device_id
HAVELLS_REGION=in  # or us, eu, cn
```

**Finding Device ID:**
```bash
# Use Tuya API Explorer or device list endpoint
# Device ID is shown in Tuya Smart app → Device Settings → Device Information
```

**Note:** Ambient lighting is optional. Practice works without smart bulb integration.

## Observability (Opik)

LLM tracing and monitoring for AI coaching calls. FretCoach uses **Comet Opik** for comprehensive LLM observability.

**Required for:** Production monitoring and optimization (optional for development)

### Setup Steps

1. **Create account:** Sign up at [comet.com/opik](https://www.comet.com/opik)
2. **Create workspace:** Set up a new workspace for FretCoach
3. **Generate API key:** Navigate to Settings → API Keys
4. **Add to .env:**

```env
OPIK_API_KEY=your_opik_key
OPIK_WORKSPACE=your_workspace_name
OPIK_PROJECT_NAME=FretCoach
OPIK_URL_OVERRIDE=https://www.comet.com/opik/api
```

### What Opik Tracks

- **Live AI Coaching:** GPT-4o-mini calls with context and responses
- **Practice Plan Generation:** Gemini 3 Flash Preview LangGraph traces
- **Web AI Coach:** Text-to-SQL agent workflows and tool calls
- **Token Usage:** Per-session and cumulative token consumption
- **Latency Metrics:** Response times and performance bottlenecks
- **Error Traces:** Failed LLM calls with full context

### Features Used

- **Tracing:** End-to-end LangChain/LangGraph execution traces
- **Agent Graphs:** Visual representation of multi-step agent workflows
- **Custom Metrics:** Practice-specific evaluation metrics
- **Dashboards:** Real-time monitoring of AI coach performance

**For detailed Opik implementation:** See [Opik Observability](opik-observability.md)

**Note:** If not configured, AI features work without observability, but you won't have visibility into LLM performance and costs.

## User ID Configuration

Required for multi-user deployments. Single-user setups can use default.

```env
USER_ID=your_unique_user_id
```

**Default:** If not set, uses `default_user`

## Deployment Configuration

Configure deployment type and debugging options.

```env
# Deployment Type (required for backend)
DEPLOYMENT_TYPE=fretcoach-studio
# To switch to portable deployment, uncomment the following line:
# DEPLOYMENT_TYPE=fretcoach-portable

# Debug Configuration (optional)
FRETCOACH_DEBUG_AUDIO=1  # Enable audio analysis debugging
```

## User Metric Preferences

FretCoach allows users to enable/disable individual metrics based on practice focus. Preferences are stored in the `user_configs` database table and persist across sessions.

### Available Metrics

- **Pitch Accuracy** (optional) - Note accuracy and intonation
- **Scale Conformity** (optional) - Adherence to target scale and fretboard coverage
- **Timing Stability** (optional) - Rhythmic consistency
- **Noise Control** (mandatory) - Always enabled as baseline quality metric

### How It Works

1. **Configuration:** Toggle metrics in Manual/AI Mode settings
2. **Storage:** Preferences saved to `user_configs` table per USER_ID
3. **Persistence:** Settings automatically applied to future sessions
4. **Adaptive Scoring:** Overall quality score recalculated from enabled metrics only
5. **AI Adaptation:** Coach feedback focuses only on tracked metrics

### Database Schema

The `user_configs` table stores:
```sql
CREATE TABLE user_configs (
    user_id TEXT PRIMARY KEY,
    pitch_accuracy BOOLEAN DEFAULT TRUE,
    scale_conformity BOOLEAN DEFAULT TRUE,
    timing_stability BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Example Use Cases:**
- **Slow practice:** Disable timing, focus on pitch + scale
- **Rhythm training:** Enable only timing stability
- **Default:** All metrics enabled for comprehensive evaluation

## Component-Specific .env Locations

FretCoach components share environment variables but require separate `.env` files.

### FretCoach Studio (Desktop App)

**Location:** `backend/.env`

**Required variables:**
```env
DB_HOST=...
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=...

OPENAI_API_KEY=...
GOOGLE_API_KEY=...
GEMINI_MODEL=gemini-3-flash-preview

# Deployment Type
DEPLOYMENT_TYPE=fretcoach-studio

# Optional - Additional AI Providers
GROQ_API_KEY=...
OPENROUTER_API_KEY=...
PPLX_API_KEY=...
TAVILY_API_KEY=...
ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
ANTHROPIC_API_KEY=...

# Optional - Smart Bulb
HAVELLS_ACCESS_ID=...
HAVELLS_ACCESS_SECRET=...
HAVELLS_DEVICE_ID=...
HAVELLS_REGION=in

# Optional - Observability
OPIK_API_KEY=...
OPIK_WORKSPACE=...
OPIK_PROJECT_NAME=FretCoach
OPIK_URL_OVERRIDE=https://www.comet.com/opik/api

# Optional - Debug
FRETCOACH_DEBUG_AUDIO=1
```

### FretCoach Hub (Web Platform)

**Backend location:** `web/web-backend/.env`

**Required variables:**
```env
# Database connection string format
DATABASE_URL=postgresql://postgres.your-project-id:your-password@aws-region.pooler.supabase.com:5432/postgres

# Or use component format
DB_HOST=...
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=...

# Model configuration
USE_OPENAI_MODEL=false
OPENAI_MODEL=gpt-4o-mini
GEMINI_MODEL=gemini-3-flash-preview

# API Keys
GOOGLE_API_KEY=...
OPENAI_API_KEY=...

# Optional - Observability
OPIK_API_KEY=...
OPIK_WORKSPACE=...
OPIK_PROJECT_NAME=FretCoach
OPIK_URL_OVERRIDE=https://www.comet.com/opik/api

# Optional - Anthropic
ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
ANTHROPIC_API_KEY=...
```

**Frontend location:** `web/web-frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8000
```

### FretCoach Portable (Raspberry Pi)

**Location:** `.env` in project root (copied to Pi)

**Required variables:**
```env
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
DB_PORT=5432
DB_NAME=...

# Deployment Type
DEPLOYMENT_TYPE=fretcoach-portable

# Optional - Smart Bulb
HAVELLS_ACCESS_ID=...
HAVELLS_ACCESS_SECRET=...
HAVELLS_DEVICE_ID=...
HAVELLS_REGION=in  # or us, eu, cn

# For AI Mode
OPENAI_API_KEY=...
GOOGLE_API_KEY=...
GEMINI_MODEL=gemini-3-flash-preview
```

## Full Template

Complete `.env` template with all variables:

```env
# Database (Supabase) - Required
DB_HOST=your_supabase_host.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_supabase_password

# AI Services - Required for AI features
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=...
GEMINI_MODEL=gemini-3-flash-preview

# Deployment Type
DEPLOYMENT_TYPE=fretcoach-studio

# Additional AI Providers - Optional
GROQ_API_KEY=...
OPENROUTER_API_KEY=...
PPLX_API_KEY=...
TAVILY_API_KEY=...
ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
ANTHROPIC_API_KEY=...

# Smart Bulb - Optional
HAVELLS_ACCESS_ID=...
HAVELLS_ACCESS_SECRET=...
HAVELLS_DEVICE_ID=...
HAVELLS_REGION=in

# Observability - Optional
OPIK_API_KEY=...
OPIK_WORKSPACE=...
OPIK_PROJECT_NAME=FretCoach
OPIK_URL_OVERRIDE=https://www.comet.com/opik/api

# Debug - Optional
FRETCOACH_DEBUG_AUDIO=1

# User ID - Optional (defaults to 'default_user')
USER_ID=...
```

## Troubleshooting

### Database connection fails

**Error:** `psycopg2.OperationalError: could not connect to server`

**Solutions:**
- Verify Supabase project is active
- Check `DB_HOST` uses full Supabase URL (includes `.supabase.co`)
- Confirm password matches Supabase project settings
- Test network connectivity to Supabase

### OpenAI API key invalid

**Error:** `openai.error.AuthenticationError: Incorrect API key`

**Solutions:**
- Regenerate key at platform.openai.com
- Ensure key starts with `sk-proj-` (new format)
- Check for whitespace in `.env` file
- Verify billing is enabled on OpenAI account

### Smart bulb not responding

**Error:** No color changes during practice

**Solutions:**
- Verify Tuya credentials in Cloud project
- Confirm `TUYA_DEVICE_ID` matches actual device
- Check bulb is online in Tuya Smart app
- Ensure correct region (`us`, `eu`, `cn`, `in`)
- Test API access in Tuya API Explorer

### Environment variables not loading

**Error:** `KeyError: 'OPENAI_API_KEY'`

**Solutions:**
- Verify `.env` file exists in correct location
- Check file is named exactly `.env` (not `env.txt` or `.env.example`)
- Restart backend server after creating/modifying `.env`
- Use absolute path verification:
  ```bash
  cat backend/.env  # Should show your variables
  ```

### Gemini API quota exceeded

**Error:** `google.generativeai.types.generation_types.BlockedPromptException`

**Solutions:**
- Check quota at [aistudio.google.com](https://aistudio.google.com)
- Free tier: 15 requests/minute, 1500 requests/day
- Reduce AI coach usage or upgrade to paid tier

## Security Notes

**Never commit `.env` files to version control.**

`.env` is gitignored by default. Verify:
```bash
git check-ignore backend/.env  # Should output: backend/.env
```

**Supabase security:**
- Use Row Level Security (RLS) for production
- Rotate database password periodically
- Limit database access to required IPs only

**API key rotation:**
- Rotate OpenAI/Gemini keys every 90 days
- Use separate keys for development/production
- Monitor usage in provider dashboards

---

**Navigation:**
- [← AI Coach Agent Engine](ai-coach-agent-engine.md)
- [Troubleshooting →](troubleshooting.md)
- [Back to Index](index.md)
