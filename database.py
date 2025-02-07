import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Get environment variables exactly as defined in Railway
PGUSER = "${{POSTGRES_USER}}"
PGPASSWORD = "${{POSTGRES_PASSWORD}}"
PGHOST = "${{RAILWAY_PRIVATE_DOMAIN}}"
PGDATABASE = "${{POSTGRES_DB}}"
PGPORT = 5432

# Construct the DATABASE_URL manually
DATABASE_URL = f"postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"

if not all([PGUSER, PGPASSWORD, PGHOST, PGDATABASE]):
    missing_vars = []
    if not PGUSER: missing_vars.append("PGUSER")
    if not PGPASSWORD: missing_vars.append("PGPASSWORD")
    if not PGHOST: missing_vars.append("PGHOST")
    if not PGDATABASE: missing_vars.append("PGDATABASE")
    raise ValueError(f"Missing required database environment variables: {', '.join(missing_vars)}")

# Configure SSL for Railway
connect_args = {
    "sslmode": "require",
    "connect_timeout": 60
}

# Create the engine with echo=True for debugging
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()