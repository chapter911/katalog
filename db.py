import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from config import Config

def get_db_connection():
    """Returns a new PyMySQL connection using DictCursor."""
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        cursorclass=DictCursor,
        autocommit=False,
        charset='utf8mb4'
    )

@contextmanager
def get_db():
    """Context manager for safe DB operations with automatic commit/rollback."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def query_db(query, args=(), one=False):
    """Convenience helper to run SELECT queries."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, args)
            results = cursor.fetchall()
            return (results[0] if results else None) if one else results

def execute_db(query, args=()):
    """Convenience helper to run INSERT/UPDATE/DELETE queries. Returns lastrowid."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, args)
            return cursor.lastrowid
