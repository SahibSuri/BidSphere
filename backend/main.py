import os
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from backend.database import SessionLocal, check_database_health
from backend.services.auth_service import bootstrap_default_admin
from backend.services.auction_service import auto_close_expired_auctions
from backend.routers import (
    auth,
    auctions,
    bids,
    watchlist,
    payments,
    notifications,
    dashboard,
    admin,
)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize database resources and default admin on startup."""
    db = SessionLocal()
    try:
        bootstrap_default_admin(db)
        auto_close_expired_auctions(db)
    except Exception as exc:
        print(f"[BidSphere Startup Warning] Database init message: {exc}")
    finally:
        db.close()
    yield


app = FastAPI(
    title="BidSphere Online Auction Management System API",
    description="Enterprise-grade REST API backend for BidSphere DBMS Project",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Sanitizes unexpected server errors, preventing internal credentials or trace leakage."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please contact the administrator.",
            "error_type": exc.__class__.__name__,
        },
    )


# System Health & Connectivity Endpoint
@app.get("/api/v1/health", tags=["System Health"])
def get_system_health():
    """Verifies backend operational status and live MySQL 8.0 connectivity."""
    db_health = check_database_health()
    overall_status = "healthy" if db_health.get("connected") else "degraded"
    return {
        "status": overall_status,
        "app_name": "BidSphere API",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database": db_health,
        "timestamp": datetime.now(timezone.utc),
    }


# Register API Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(auctions.router, prefix="/api/v1")
app.include_router(bids.router, prefix="/api/v1")
app.include_router(watchlist.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
