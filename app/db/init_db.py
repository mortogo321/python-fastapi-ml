from sqlalchemy import text

from app.core.logging_config import logger
from app.db.base import Base, engine


def init_db() -> None:
    """Initialize database with pgvector extension and create tables."""
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            logger.info("pgvector extension enabled")

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

    except Exception as e:
        logger.error("Error initializing database: %s", e)
        raise


if __name__ == "__main__":
    init_db()
