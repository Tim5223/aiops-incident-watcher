import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Reads the DB connection string from an environment variable.
# In docker-compose, this points to the "db" service by name (not localhost),
# since containers talk to each other using their service name as the hostname.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://watcher:watcherpass@db:5432/watcherdb",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session, closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
