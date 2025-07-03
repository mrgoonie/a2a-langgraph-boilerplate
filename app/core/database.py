from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Import for setting up relationships after all models are loaded
from app.models.setup_relationships import setup_relationships

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine_args = {}
if not DATABASE_URL.startswith("sqlite"):
    engine_args["pool_size"] = 100
    engine_args["pool_timeout"] = 30

engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Set up relationships after all models are loaded
setup_relationships()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
