import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

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
    try:
        yield db
    finally:
        db.close()
