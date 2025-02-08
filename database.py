import os
import psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection URL
DATABASE_URL = "postgresql://postgres:FIeQmkQFLeMMQiVXMbketFGPUZpGfUnA@postgres.railway.internal:5432/railway"

@contextmanager
def get_db():
    """Context manager for database connection."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def execute_query(query, params=None):
    """Execute a database query."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()

def fetch_results(query, params=None):
    """Fetch results from a database query."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()