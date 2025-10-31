from sqlalchemy import text
from app.db.base import engine, Base
from app.core.logging_config import logger


def init_db():
    """Initialize database with pgvector extension and create tables."""
    try:
        # Enable pgvector extension
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            logger.info("pgvector extension enabled")

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


if __name__ == "__main__":
    init_db()
