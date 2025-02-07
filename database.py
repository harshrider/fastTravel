import os
import psycopg2
from psycopg2 import sql
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve database connection parameters from environment variables
PGHOST = os.getenv('PGHOST')
PGPORT = os.getenv('PGPORT', '5432')  # Default to 5432 if not set
PGUSER = os.getenv('PGUSER')
PGPASSWORD = os.getenv('PGPASSWORD')
PGDATABASE = os.getenv('PGDATABASE')

# Create a connection string
DATABASE_URL = f"postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"

# Establish a connection to the PostgreSQL database
@contextmanager
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

# Function to execute a query
def execute_query(query, params=None):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()

# Function to fetch results from a query
def fetch_results(query, params=None):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
