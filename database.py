# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Check if the database URL is for SQLite
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {"sslmode": "require"}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarative class
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# # database.py
# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from dotenv import load_dotenv
#
# load_dotenv()
#
# # Get the database URL from the environment variable set by the service connector
# DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRESQLCONNSTR_<name>")
# if not DATABASE_URL:
#     raise ValueError("Database URL not found in environment variables")
#
# # SSL Configuration if required
# connect_args = {"sslmode": "require"}
#
# engine = create_engine(DATABASE_URL, connect_args=connect_args)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# # Base declarative class
# from sqlalchemy.ext.declarative import declarative_base
# Base = declarative_base()
#
# # Dependency for database session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
