from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database Configuration
# Use environment variable to switch between local and production databases
USE_LOCAL_DB = os.getenv("USE_LOCAL_DB", "true").lower() == "true"

if USE_LOCAL_DB:
    # Local SQLite database for development
    DATABASE_URL = "sqlite:///./apartments.db"
    print("📁 Using local SQLite database for development")
else:
    # AWS RDS PostgreSQL Database for production
    DATABASE_URL = "postgresql://postgres:yvnreddy2002@flatfund-db.ctqftasebvp9.ap-south-1.rds.amazonaws.com:5432/postgres"
    print("🌐 Using AWS RDS PostgreSQL database")

# Engine configuration
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
