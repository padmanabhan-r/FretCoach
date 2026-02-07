# FretCoach Hub - Web Frontend

React dashboard for practice analytics and AI coaching. Live at [fretcoach.online](https://www.fretcoach.online)

## What is this?

Web interface for reviewing practice sessions, viewing performance trends, and chatting with an AI coach about your guitar progress.

## Tech Stack

- React 18 + TypeScript + Vite
- Tailwind CSS + shadcn/ui
- TanStack React Query (state management)
- Recharts (data visualization)
- Deployed on Vercel

## Quick Start

```bash
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
npm run dev  # Runs at http://localhost:5173
```

Backend must be running at the URL in `VITE_API_BASE_URL`.

## Production

```bash
npm run build  # Outputs to dist/
```

Deployed to Vercel with auto-deploy from `main` branch.

**Production repo:** [github.com/padmanabhan-r/FretCoach-Web-Frontend](https://github.com/padmanabhan-r/FretCoach-Web-Frontend)

## Documentation

See [docs/web-dashboard.md](../../docs/web-dashboard.md) for detailed usage and architecture.
