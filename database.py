# database.py
import os
import psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

# Get directly from Railway's environment variable
DATABASE_URL = "postgresql://postgres:FIeQmkQFLeMMQiVXMbketFGPUZpGfUnA@postgres.railway.internal:5432/railway"

@contextmanager
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

# Function to execute a query
def execute_query(query, params=None):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()

# Function to fetch results from a query
def fetch_results(query, params=None):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
