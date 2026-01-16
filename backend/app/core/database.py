from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from app.core.config import settings

# Create engine with optimized settings for Supabase/cloud PostgreSQL
engine = create_engine(
    settings.database_url_with_options,
    pool_pre_ping=settings.DB_POOL_PRE_PING,  # Check connection health before use
    pool_size=settings.DB_POOL_SIZE,  # Number of connections to maintain
    max_overflow=settings.DB_MAX_OVERFLOW,  # Additional connections when pool is full
    poolclass=QueuePool,
    # Connection settings optimized for cloud environments
    connect_args={
        "connect_timeout": 10,  # Connection timeout in seconds
        "options": "-c statement_timeout=30000",  # 30s query timeout
    } if "supabase" in settings.DATABASE_URL.lower() else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """Health check for database connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
