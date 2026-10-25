import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "bidsphere_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "bidsphere_pass")
DB_NAME = os.getenv("DB_NAME", "bidsphere_db")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?charset=utf8mb4"
)

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency for managing database session lifecycle."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_health() -> dict:
    """Verifies live MySQL connectivity and returns connection metadata."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION() AS version, DATABASE() AS current_db")).fetchone()
            return {
                "status": "healthy",
                "connected": True,
                "version": result.version if result else "Unknown",
                "database": result.current_db if result else "Unknown",
                "host": DB_HOST,
                "port": int(DB_PORT),
            }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(exc),
            "host": DB_HOST,
            "port": int(DB_PORT),
        }
