"""
Database connection pooling utilities
"""
import sqlite3
import threading
from contextlib import contextmanager
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Thread-local storage for SQLite connections
_local = threading.local()


@contextmanager
def get_db_connection(db_path: str, timeout: float = 5.0):
    """
    Context manager for database connections with connection pooling
    
    Uses thread-local connections to SQLite for better concurrency
    """
    if not hasattr(_local, 'connection') or _local.connection is None:
        _local.connection = sqlite3.connect(
            db_path,
            timeout=timeout,
            check_same_thread=False  # Allow thread-local connections
        )
        _local.connection.row_factory = sqlite3.Row  # Return dict-like rows
    
    conn = _local.connection
    
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        # Don't close - keep connection alive for thread
        pass


def close_db_connections():
    """Close all thread-local database connections"""
    if hasattr(_local, 'connection') and _local.connection:
        try:
            _local.connection.close()
        except Exception:
            pass
        _local.connection = None

