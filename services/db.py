from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
import logging
from config import config

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# DB Setup
Base = declarative_base()
engine = create_engine(config.DATABASE_URL, pool_pre_ping=True)  # Enable health checks
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initialize the database by creating all tables defined in models.
    """
    try:
        logging.info("Initializing database...")
        Base.metadata.create_all(bind=engine)
        logging.info("Database initialized successfully.")
    except SQLAlchemyError as e:
        logging.error(f"Failed to initialize the database: {e}")
        raise


def get_db():
    """
    Dependency for obtaining a SQLAlchemy session.
    Ensures proper cleanup of session resources.
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logging.error(f"Database operation failed: {e}")
        raise
    finally:
        db.close()
        logging.info("Database session closed.")
