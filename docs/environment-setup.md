# Environment Setup

Complete environment configuration guide for all FretCoach components.

## Prerequisites

- **Python 3.12+** (required for all backend components)
- **Node.js 18+** and npm (required for frontend applications)
- **PostgreSQL** access (Supabase recommended)

## Quick Start

Each component requires a `.env` file with specific credentials. Follow the sections below to configure your setup.

## Database Configuration (Supabase)

FretCoach uses PostgreSQL hosted on Supabase for session tracking, practice plans, and user preferences.

**Required for:** All components (Studio, Hub, Portable)

### Setup Steps

1. **Create Supabase project** at [supabase.com](https://supabase.com)

2. **Run schema creation script:**
   ```bash
   psql -h your_host -U postgres -d postgres -f backend/sql/fretcoach_supabase_schema.sql
   ```
   Or copy the contents into Supabase SQL Editor and run it.

3. **Add credentials to `.env`:**
   ```env
   DB_HOST=your_supabase_host.supabase.co
   DB_PORT=5432
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASSWORD=your_supabase_password
   ```

**Note:** Session logging is optional. If database is unavailable, practice sessions continue without persistence.

## AI Services API Keys

**Required for:** AI Practice Mode, Live Coaching, Hub Chat

### OpenAI
For GPT-4o-mini (text) and GPT-4o-mini-TTS (voice coaching).

Get API key: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

```env
OPENAI_API_KEY=sk-proj-...
```

### Google Gemini
For practice plans and Hub chat agent.

Get API key: [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

```env
GOOGLE_API_KEY=...
GEMINI_MODEL=gemini-3-flash-preview
```

### Anthropic via Minimax (Optional)
Fallback model for rate-limited scenarios.

```env
ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
ANTHROPIC_API_KEY=...
```

## Smart Bulb Setup (Optional)

Ambient lighting provides real-time sensory feedback during practice.

**Compatible devices:** Any Tuya-compatible smart bulb

**Setup:**
1. Connect bulb to Tuya Smart app
2. Create developer account at [iot.tuya.com](https://iot.tuya.com)
3. Create Cloud Project and get credentials

```env
HAVELLS_ACCESS_ID=...
HAVELLS_ACCESS_SECRET=...
HAVELLS_DEVICE_ID=...
HAVELLS_REGION=in  # or us, eu, cn
```

**Note:** Completely optional. Leave blank to disable.

## Observability (Opik)

**Comet Opik** provides LLM tracing and monitoring for AI coaching features.

**Required for:** Production monitoring (optional for development)

### Quick Setup

1. Create account at [comet.com/opik](https://www.comet.com/opik)
2. Generate API key from Settings → API Keys
3. Add to `.env`:

```env
OPIK_API_KEY=your_opik_key
OPIK_WORKSPACE=your_workspace_name
OPIK_PROJECT_NAME=FretCoach
OPIK_URL_OVERRIDE=https://www.comet.com/opik/api
```

**What's tracked:** LLM calls, token usage, latency, errors, and agent workflows.

**For detailed implementation:** See [Opik Observability](opik-observability.md)

**Note:** If not configured, AI features work normally without observability.

## Additional Configuration

```env
# User ID (optional - defaults to 'default_user')
USER_ID=your_unique_user_id

# Deployment Type (required)
DEPLOYMENT_TYPE=fretcoach-studio  # or fretcoach-portable

# Debug Audio Analysis (optional)
FRETCOACH_DEBUG_AUDIO=1
```


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

# Optional - Fallback AI Provider
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

# Fallback AI Provider - Optional
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

**Database connection fails:**
- Verify Supabase project is active and credentials are correct
- Check `DB_HOST` includes `.supabase.co`

**API key invalid:**
- Regenerate key from provider dashboard
- Check for whitespace in `.env` file
- Verify billing is enabled (if required)

**Environment variables not loading:**
- Verify `.env` file exists in correct location (`backend/.env` or `web/web-backend/.env`)
- Restart backend server after modifying `.env`

**Smart bulb not responding:**
- Leave `HAVELLS_*` variables blank to disable (completely optional)

## Security Notes

- **Never commit `.env` files** — gitignored by default
- **Rotate API keys periodically** — Use separate keys for dev/production
- **Supabase:** Enable Row Level Security (RLS) for production

---

**Navigation:**
- [← AI Coach Agent Engine](ai-coach-agent-engine.md)
- [Troubleshooting →](troubleshooting.md)
- [Back to Index](index.md)
