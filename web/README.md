# FretCoach Dashboard

A web-based dashboard for FretCoach that displays real-time practice session metrics and includes an AI Practice Coach for personalized guidance.

## Features

- **Real-time Dashboard**: View your practice session metrics including pitch accuracy, scale conformity, and timing stability
- **Session History**: Browse and analyze individual practice sessions
- **AI Practice Coach**: Chat with an AI coach that can:
  - Analyze your performance trends
  - Generate personalized practice recommendations
  - Show interactive charts and visualizations
  - Compare your latest session to your average

## Tech Stack

- **Frontend**: React + Vite + TypeScript
- **UI Components**: shadcn/ui + Tailwind CSS
- **Charts**: Recharts
- **State Management**: TanStack React Query
- **Backend**: Vercel Serverless Functions
- **Database**: PostgreSQL
- **AI**: OpenAI GPT-4o-mini with function calling

## Setup

### Prerequisites

- Node.js 18+
- PostgreSQL database with FretCoach sessions table
- OpenAI API key

### Installation

1. Install dependencies:
   ```bash
   cd web
   npm install
   ```

2. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Configure your environment variables:
   ```env
   # Database
   DATABASE_URL=postgresql://username:password@host:5432/fretcoach

   # OpenAI
   OPENAI_API_KEY=sk-your-api-key

   # Optional: Opik for LLM tracing
   OPIK_API_KEY=your-opik-key
   ```

### Development

Run the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:8080`

**Note**: The API routes (`/api/*`) require Vercel CLI for local development:
```bash
npm install -g vercel
vercel dev
```

### Build

Build for production:
```bash
npm run build
```

## Deployment to Vercel

This project is designed to be self-contained and deployable to Vercel:

1. Push to GitHub
2. Import the `web` folder in Vercel
3. Set environment variables in Vercel dashboard:
   - `DATABASE_URL`
   - `OPENAI_API_KEY`
   - `OPIK_API_KEY` (optional)
4. Deploy

The `vercel.json` configuration handles routing for both the SPA and API routes.

## API Routes

### GET `/api/sessions`

Fetch practice sessions from the database.

**Query Parameters:**
- `user_id` (string): User identifier (default: "default_user")
- `limit` (number): Number of sessions to fetch (default: 10)
- `include_aggregates` (boolean): Include aggregate statistics (default: true)

**Response:**
```json
{
  "success": true,
  "sessions": [...],
  "aggregates": {
    "total_sessions": 10,
    "avg_pitch_accuracy": 0.85,
    "avg_scale_conformity": 0.78,
    "avg_timing_stability": 0.82,
    "total_practice_time": 3600,
    "scales_practiced": ["C Major", "G Major"]
  }
}
```

### POST `/api/chat`

Send a message to the AI Practice Coach.

**Request Body:**
```json
{
  "messages": [
    { "role": "user", "content": "Show me my progress" }
  ],
  "user_id": "default_user",
  "thread_id": "optional-thread-id"
}
```

**Response:**
```json
{
  "success": true,
  "message": {
    "role": "assistant",
    "content": "Here's your performance data..."
  },
  "chartData": {
    "type": "performance_trend",
    "data": [...]
  }
}
```

## AI Coach Tools

The AI Coach has access to the following tools:

1. **get_performance_chart**: Generates interactive charts showing performance trends
2. **get_practice_recommendation**: Creates personalized practice plans
3. **get_session_comparison**: Compares latest session to average performance

## Opik Tracing

LLM calls are automatically traced with Opik when configured. Thread IDs are used to group related chat messages into conversations.

## Project Structure

```
web/
├── api/                    # Vercel serverless functions
│   ├── sessions.ts         # Sessions API endpoint
│   └── chat.ts             # AI Coach chat endpoint
├── src/
│   ├── components/
│   │   ├── ui/             # shadcn/ui components
│   │   └── charts/         # Chart components
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utilities and API client
│   ├── pages/              # Page components
│   └── integrations/       # Third-party integrations
├── public/                 # Static assets
├── .env.example            # Environment variables template
├── vercel.json             # Vercel configuration
└── package.json
```

## License

MIT
