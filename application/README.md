# FretCoach Desktop Application

A beautiful React-based Electron desktop application for FretCoach guitar learning.

## Installation

```bash
npm install
```

## Development

```bash
# Start the development server
npm run dev
```

This will start both the Vite dev server and Electron in development mode.

## Building

```bash
# Build for production
npm run build

# Package for your platform
npm run package

# Or platform-specific
npm run package:mac
npm run package:win
npm run package:linux
```

## Structure

- `src/` - React components (JSX)
- `electron/` - Electron main and preload scripts
- `dist/` - Build output
- `release/` - Packaged applications
