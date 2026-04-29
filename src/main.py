"""
FastAPI application — serves the API and the frontend static files.
"""

import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.config import GROK_API_KEY
from src.models import ParseRequest, ParseResponse
from src.parser import parse_mom_message

# ── Logging ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── App ─────────────────────────────────────────────────────────
app = FastAPI(
    title="Mumzworld Shopping List Parser",
    description="Turn a mom's messy text or voice message into a structured shopping list and calendar.",
    version="1.0.0",
)

# CORS — allow the frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── API Routes ──────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "api_key_configured": bool(GROK_API_KEY),
    }


@app.post("/api/parse", response_model=ParseResponse)
async def parse_message(request: ParseRequest):
    """
    Parse a mom's message into structured shopping items and calendar events.

    Accepts text in English or Arabic. Returns structured JSON with
    confidence scores and uncertainty flags.
    """
    if not GROK_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Grok API key is not configured. Set GROK_API_KEY in your .env file.",
        )

    logger.info(f"Parsing message ({len(request.message)} chars)")

    try:
        result = await parse_mom_message(
            message=request.message,
            language_hint=request.language_hint,
        )
        return result
    except Exception as e:
        logger.error(f"Parse failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your message: {str(e)}",
        )


# ── Static Files (Frontend) ────────────────────────────────────

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


@app.get("/")
async def serve_frontend():
    """Serve the main HTML page."""
    return FileResponse(FRONTEND_DIR / "index.html")


# Mount static files for CSS and JS
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# ── Entry point ─────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    from src.config import APP_HOST, APP_PORT

    uvicorn.run(
        "src.main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=True,
    )
