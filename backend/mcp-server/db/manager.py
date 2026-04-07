"""
Singleton Database Manager with thread-safe connection pooling.
Production-grade pattern for fintech applications.
"""

import sqlite3
import threading
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
import config


class DatabaseManager:
    """
    Thread-safe singleton database manager.

    Features:
    - Single instance across all MCP tools
    - Thread-local connections (one per thread)
    - Context manager for transactions
    - Automatic rollback on errors
    """

    _instance: Optional['DatabaseManager'] = None
    _lock = threading.Lock()

    def __new__(cls):
        """Ensure only one instance is created (thread-safe)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize database manager (only once)."""
        if not hasattr(self, 'initialized'):
            self.db_path = config.DB_PATH
            self._local = threading.local()
            self.initialized = True
            print(f"🔗 DatabaseManager initialized: {self.db_path}")

    @property
    def connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row  # Return rows as dicts
            print(f"🔌 New connection created for thread {threading.current_thread().name}")
        return self._local.conn

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.

        Usage:
            with db.transaction() as conn:
                conn.execute("INSERT INTO ...")
        """
        conn = self.connection
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"❌ Transaction rolled back: {e}")
            raise

    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute SELECT query and return results."""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def execute_one(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Execute SELECT query and return single result."""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def close(self):
        """Close thread-local connection."""
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
            delattr(self._local, 'conn')
            print(f"🔌 Connection closed for thread {threading.current_thread().name}")

    @classmethod
    def get_instance(cls) -> 'DatabaseManager':
        """Get singleton instance."""
        return cls()


# Convenience function for quick access
def get_db() -> DatabaseManager:
    """Get database manager instance."""
    return DatabaseManager.get_instance()
