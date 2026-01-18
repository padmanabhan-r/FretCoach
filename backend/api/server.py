"""
FastAPI server for FretCoach
Provides REST API endpoints for the Electron app to communicate with the Python backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import devices, config, session, metrics, scales, ai_mode, live_coach

app = FastAPI(title="FretCoach API")

# Enable CORS for Electron app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(devices.router, tags=["devices"])
app.include_router(config.router, tags=["config"])
app.include_router(session.router, tags=["session"])
app.include_router(metrics.router, tags=["metrics"])
app.include_router(scales.router, tags=["scales"])
app.include_router(ai_mode.router, tags=["ai"])
app.include_router(live_coach.router, tags=["live-coach"])


@app.get("/")
async def root():
    """API root endpoint"""
    return {"message": "FretCoach API", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

#uvicorn backend.api.server:app --reload --host 127.0.0.1 --port 8000