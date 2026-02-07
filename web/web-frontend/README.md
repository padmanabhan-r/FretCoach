# FretCoach Hub - Web Frontend

React-based web dashboard for practice analytics, session review, and AI coaching.

**Live Deployment:** [fretcoach.online](https://www.fretcoach.online)

---

## Overview

FretCoach Hub is the web-based analytics and coaching platform for FretCoach. It provides practice session visualization, trend analysis, and an AI-powered conversational coach that answers questions about your playing progress.

**This is the frontend component** — the React application deployed to Vercel. For the backend API, see [web-backend/](../web-backend/).

---

## Key Features

### 1. Practice Analytics Dashboard
- **Session History:** View all practice sessions with detailed metrics
- **Performance Trends:** Charts showing improvement over time
- **Metric Breakdown:** Drill down into pitch accuracy, scale conformity, timing stability
- **Weekly/Monthly Views:** Compare performance across different time periods

### 2. AI Chat Coach
- **Natural Language Queries:** Ask questions like "What's my weakest metric?" or "Show progress this week"
- **Database-Grounded Responses:** LangGraph agent with text-to-SQL capabilities
- **Powered by Gemini 2.5 Flash:** Fast, intelligent coaching responses
- **Session Context:** Coach knows your full practice history

### 3. Practice Plan Generator
- **AI-Recommended Sessions:** Get personalized practice recommendations
- **Weakness Targeting:** Plans focus on your identified weak areas
- **Difficulty Adaptation:** Adjusts strictness and sensitivity to your level

---

## Tech Stack

**Frontend Framework:**
- **React 18** — UI component library with hooks
- **TypeScript** — Type-safe JavaScript
- **Vite** — Fast build tool and dev server
- **Tailwind CSS** — Utility-first styling
- **shadcn/ui** — Pre-built accessible components (built on Radix UI)

**State Management:**
- **TanStack React Query** — Server state management and caching
- **React Router v6** — Client-side routing

**Data Visualization:**
- **Recharts** — Composable charting library

**Deployment:**
- **Vercel** — Frontend hosting with CDN and edge caching

---

## Project Structure

```
web-frontend/
├── src/
│   ├── components/        # Reusable UI components
│   ├── pages/             # Route-based page components
│   ├── services/          # API client for backend
│   ├── hooks/             # Custom React hooks
│   ├── utils/             # Helper functions
│   ├── types/             # TypeScript type definitions
│   └── App.tsx            # Root application component
│
├── public/                # Static assets
├── index.html             # HTML entry point
├── vite.config.ts         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
└── tsconfig.json          # TypeScript configuration
```

---

## Installation

### Prerequisites
- Node.js 18+
- npm or yarn

### Setup

```bash
# Clone the repository
git clone https://github.com/padmanabhan-r/FretCoach.git
cd FretCoach/web-frontend

# Install dependencies
npm install

# Create .env file (see Environment Variables section)
cp .env.example .env
```

---

## Environment Variables

Create a `.env` file in the `web-frontend/` directory:

```env
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000

# Optional: Analytics
VITE_ANALYTICS_ID=your_analytics_id
```

**For production (Vercel):**
- Set `VITE_API_BASE_URL` to your Railway backend URL
- Environment variables configured in Vercel dashboard

---

## Development

```bash
# Start development server
npm run dev
```

Runs the app at **http://localhost:5173** with hot module replacement.

**Backend Required:** Ensure the backend API is running at the URL specified in `VITE_API_BASE_URL`.

---

## Building for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build locally
npm run preview
```

Output is generated in `dist/` directory.

---

## Deployment

### Vercel (Recommended)

This project is configured for automatic deployment to Vercel:

1. **Connect GitHub Repository:**
   - Import project in Vercel dashboard
   - Link to your fork/repo

2. **Configure Build Settings:**
   - Framework Preset: **Vite**
   - Build Command: `npm run build`
   - Output Directory: `dist`

3. **Set Environment Variables:**
   - Add `VITE_API_BASE_URL` pointing to your Railway backend

4. **Deploy:**
   - Every push to `main` triggers auto-deployment

**Production URL:** [fretcoach.online](https://www.fretcoach.online)

---

## API Integration

The frontend communicates with the FretCoach Hub backend (FastAPI) via REST API:

**Key Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/sessions` | GET | Fetch user practice sessions |
| `/sessions/{id}` | GET | Get session details |
| `/analytics/trends` | GET | Get performance trend data |
| `/chat` | POST | Send message to AI coach |
| `/practice-plans` | GET | Get AI-generated practice plans |

**API Client:** See `src/services/api.ts` for full API abstraction.

---

## Pages & Routes

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | `Home` | Landing page with product overview |
| `/dashboard` | `Dashboard` | Main analytics dashboard |
| `/sessions` | `Sessions` | Session history list |
| `/sessions/:id` | `SessionDetail` | Detailed session view |
| `/coach` | `AICoach` | Conversational AI coach interface |
| `/practice-plans` | `PracticePlans` | AI-recommended practice sessions |

---

## Key Components

**Analytics:**
- `TrendChart` — Line charts for performance over time
- `MetricCard` — Individual metric display (pitch, timing, scale)
- `SessionTable` — Tabular session history

**AI Coach:**
- `ChatInterface` — Chat UI for conversational coach
- `MessageBubble` — Individual message display
- `QuerySuggestions` — Pre-built query buttons

**Shared:**
- `Header` — Navigation bar
- `Sidebar` — Dashboard navigation
- `LoadingSpinner` — Loading states
- `ErrorBoundary` — Error handling

---

## Styling

**Tailwind CSS:**
- Utility-first approach
- Configured in `tailwind.config.js`
- Custom color palette for FretCoach brand

**shadcn/ui Components:**
- Pre-built accessible components
- Customizable via `components.json`
- Built on Radix UI primitives

**Responsive Design:**
- Mobile-first approach
- Breakpoints: `sm`, `md`, `lg`, `xl`, `2xl`

---

## State Management

**TanStack React Query (formerly React Query):**

- **Server State:** All API data fetched and cached via React Query
- **Query Keys:** Organized by feature (`sessions`, `analytics`, `coach`)
- **Automatic Refetching:** Stale data refreshed on window focus
- **Optimistic Updates:** UI updates before server confirmation

**Example:**
```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['sessions', userId],
  queryFn: () => fetchSessions(userId),
  staleTime: 5 * 60 * 1000, // 5 minutes
});
```

---

## TypeScript

**Type Safety:**
- All components, hooks, and utilities are fully typed
- API response types defined in `src/types/`
- Strict mode enabled in `tsconfig.json`

**Key Types:**

```typescript
interface Session {
  id: string;
  user_id: string;
  timestamp: string;
  scale_name: string;
  scale_type: string;
  metrics: {
    pitch_accuracy: number;
    scale_conformity: number;
    timing_stability: number;
    noise_control: number;
  };
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}
```

---

## Testing

```bash
# Run tests (if configured)
npm run test

# Type checking
npm run type-check

# Linting
npm run lint
```

**Testing Stack:**
- Vitest (planned)
- React Testing Library (planned)

---

## Troubleshooting

### API Connection Failed

**Issue:** `Failed to fetch` or CORS errors

**Solutions:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify `VITE_API_BASE_URL` in `.env`
3. Ensure CORS is configured in backend to allow frontend origin

---

### Build Errors

**Issue:** TypeScript errors during build

**Solutions:**
1. Run `npm install` to ensure dependencies are up-to-date
2. Check `tsconfig.json` for strict settings
3. Fix type errors reported in terminal

---

### Slow Development Server

**Issue:** Vite dev server slow or unresponsive

**Solutions:**
1. Clear Vite cache: `rm -rf node_modules/.vite`
2. Restart dev server
3. Check for infinite render loops in components

---

## Production Repositories

**Note:** This is a monorepo reference implementation. The **production deployment** uses separate repositories:

- **Frontend:** [github.com/padmanabhan-r/FretCoach-Web-Frontend](https://github.com/padmanabhan-r/FretCoach-Web-Frontend)
- **Backend:** [github.com/padmanabhan-r/FretCoach-Web-Backend](https://github.com/padmanabhan-r/FretCoach-Web-Backend)

**Why separate?** Automated deployments to Vercel (frontend) and Railway (backend) via GitHub Actions.

---

## Documentation

For detailed architecture and usage:
- [Web Dashboard Guide](../docs/web-dashboard.md)
- [System Architecture](../docs/architecture.md#component-2-web-platform)
- [Environment Setup](../docs/environment-setup.md)

---

## Contributing

Contributions welcome! Please see [Contributing Guidelines](../README.md#contributing) in the main README.

**Areas for Contribution:**
- UI/UX improvements
- New chart types for analytics
- Accessibility enhancements
- Performance optimizations

---

## License

Open source — see [LICENSE](../LICENSE) in repository root.

---

**Built with React ⚛️ | Powered by FretCoach 🎸**
