# database.py
import os
<<<<<<< HEAD
import psycopg2
from contextlib import contextmanager
=======
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
>>>>>>> parent of fc00cf5 (updating database var)
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


<<<<<<< HEAD
load_dotenv()

# Get directly from Railway's environment variable
DATABASE_URL = "postgresql://postgres:FIeQmkQFLeMMQiVXMbketFGPUZpGfUnA@postgres.railway.internal:5432/railway"

@contextmanager
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
=======
load_dotenv()  # Load environment variables from .env file

# Get environment variables from the Railway-provided .env
PGUSER = os.getenv('PGUSER')  # Username (from Railway)
PGPASSWORD = os.getenv('PGPASSWORD')  # Password (from Railway)
PGHOST = os.getenv('PGHOST')  # Host (RAILWAY_PRIVATE_DOMAIN or custom host)
PGPORT = os.getenv('PGPORT')  # Port (5432 by default, from Railway)
PGDATABASE = os.getenv('PGDATABASE')  # Database name (from Railway)

# Ensure all required environment variables are set
if not all([PGUSER, PGPASSWORD, PGHOST, PGDATABASE, PGPORT]):
    missing_vars = []
    if not PGUSER: missing_vars.append("PGUSER")
    if not PGPASSWORD: missing_vars.append("PGPASSWORD")
    if not PGHOST: missing_vars.append("PGHOST")
    if not PGDATABASE: missing_vars.append("PGDATABASE")
    if not PGPORT: missing_vars.append("PGPORT")
    raise ValueError(f"Missing required database environment variables: {', '.join(missing_vars)}")

# Construct the DATABASE_URL using the environment variables
DATABASE_URL = f"postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"

# Configure SSL for Railway (optional, but generally required in production)
connect_args = {
    "sslmode": "require",
    "connect_timeout": 60
}

# Create the SQLAlchemy engine with the DATABASE_URL and connection arguments
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=True,  # Set to True for debugging queries
    pool_size=5,
    max_overflow=10,
    pool_timeout=30
)

# Set up session maker and declarative base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for database session"""
    db = SessionLocal()
>>>>>>> parent of fc00cf5 (updating database var)
    try:
        yield db
    finally:
<<<<<<< HEAD
        conn.close()
#DATABASE_URL = "postgresql://user:password@localhost/dbname"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
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
=======
        db.close()
>>>>>>> parent of fc00cf5 (updating database var)
