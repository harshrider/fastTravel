import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Get the database URL from the environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Ensure DATABASE_URL is set; raise an error if not found
if not DATABASE_URL:
    raise ValueError("Database URL not found in environment variables")

# Create the SQLAlchemy engine with SSL mode for non-SQLite URLs
connect_args = {"sslmode": "require"} if DATABASE_URL.startswith("postgresql") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarative class for the ORM
Base = declarative_base()

# Dependency to provide a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
