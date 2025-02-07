import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Get environment variables from Railway
PGUSER = os.getenv('POSTGRES_USER')  # Username from Railway
PGPASSWORD = os.getenv('POSTGRES_PASSWORD')  # Password from Railway
PGHOST = os.getenv('RAILWAY_TCP_PROXY_DOMAIN')  # Host from Railway (Private DNS of the service)
PGPORT = os.getenv('RAILWAY_TCP_PROXY_PORT')  # Port for the database (from Railway's proxy)
PGDATABASE = os.getenv('POSTGRES_DB')  # Database name from Railway

# Ensure all required environment variables are set
if not all([PGUSER, PGPASSWORD, PGHOST, PGDATABASE, PGPORT]):
    missing_vars = []
    if not PGUSER: missing_vars.append("POSTGRES_USER")
    if not PGPASSWORD: missing_vars.append("POSTGRES_PASSWORD")
    if not PGHOST: missing_vars.append("RAILWAY_TCP_PROXY_DOMAIN")
    if not PGDATABASE: missing_vars.append("POSTGRES_DB")
    if not PGPORT: missing_vars.append("RAILWAY_TCP_PROXY_PORT")
    raise ValueError(f"Missing required database environment variables: {', '.join(missing_vars)}")

# Construct the DATABASE_URL manually
DATABASE_URL = f"postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"

# Configure SSL for Railway
connect_args = {
    "sslmode": "require",
    "connect_timeout": 60
}

# Create the SQLAlchemy engine with the database URL and connection arguments
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=True,  # Set to True for debugging queries
    pool_size=5,
    max_overflow=10,
    pool_timeout=30
)

# Set up the session maker and declarative base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
