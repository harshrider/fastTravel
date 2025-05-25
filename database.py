import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Determine environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")  # local, production

if ENVIRONMENT == "production":
    # PythonAnywhere MySQL
    DATABASE_URL = "mysql+pymysql://harshrider:yourpassword@harshrider.mysql.pythonanywhere-services.com/harshrider$yourdbname"
else:
    # Local SQLite for development
    DATABASE_URL = "sqlite:///./travel_app.db"

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found")

# SQLite needs different settings
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()