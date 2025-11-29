"""Database configuration module.

Supports SQLite and PostgreSQL. Use DATABASE_URL environment variable to select:
- SQLite (default): DATABASE_URL not set or "sqlite:///data.db"
- PostgreSQL: DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
"""
import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_sqlalchemy import Base, User

# Get database URL from environment or default to SQLite
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data.db')


def get_engine(database_url: Optional[str] = None, echo: bool = False):
    """Create and return a SQLAlchemy engine.
    
    Args:
        database_url: Database URL (uses DATABASE_URL env var if None)
        echo: Whether to log all SQL statements
    
    Returns:
        SQLAlchemy Engine instance
    """
    url = database_url or DATABASE_URL
    
    # For SQLite, no special options needed
    if url.startswith('sqlite://'):
        return create_engine(url, echo=echo, future=True)
    
    # For PostgreSQL, add connection pool and other settings
    if url.startswith('postgresql://') or url.startswith('postgres://'):
        return create_engine(
            url,
            echo=echo,
            future=True,
            pool_pre_ping=True,  # Test connection before using from pool
            pool_size=10,
            max_overflow=20,
        )
    
    # Fallback to default creation
    return create_engine(url, echo=echo, future=True)


def init_db(database_url: Optional[str] = None):
    """Initialize database schema.
    
    Creates all tables defined in Base.metadata if they don't exist.
    
    Args:
        database_url: Database URL (uses DATABASE_URL env var if None)
    
    Returns:
        Tuple of (engine, Session class)
    """
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, future=True)
    return engine, Session


def drop_all(database_url: Optional[str] = None):
    """Drop all tables from the database.
    
    WARNING: This deletes all data. Use only in testing/development.
    
    Args:
        database_url: Database URL (uses DATABASE_URL env var if None)
    """
    engine = get_engine(database_url)
    Base.metadata.drop_all(engine)
