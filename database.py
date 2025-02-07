import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Construct the DATABASE_URL using individual environment variables
PGUSER = os.getenv("POSTGRES_USER", "postgres")
PGPASSWORD = os.getenv("POSTGRES_PASSWORD")
PGHOST = os.getenv("RAILWAY_PRIVATE_DOMAIN")
PGDATABASE = os.getenv("POSTGRES_DB", "railway")
PGPORT = os.getenv("PGPORT", "5432")

# Construct the DATABASE_URL manually
DATABASE_URL = f"postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"

if not all([PGUSER, PGPASSWORD, PGHOST, PGDATABASE]):
    raise ValueError("Missing required database environment variables")

# Configure SSL for Railway
connect_args = {
    "sslmode": "require",
    "connect_timeout": 60  # Adding a connection timeout
}

# Create the engine with echo=True for debugging
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=True,  # Enable SQL query logging
    pool_size=5,  # Set connection pool size
    max_overflow=10,  # Maximum number of connections that can be created beyond pool_size
    pool_timeout=30  # Timeout for getting a connection from the pool
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()