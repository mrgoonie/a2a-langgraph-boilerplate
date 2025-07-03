import os
from sqlalchemy import create_engine, MetaData, inspect, text
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

# Explicitly set the database connection string
DATABASE_URL = "postgresql://postgres:postgresql@127.0.0.1:5432/a2a-langgraph-boilerplate"

# Create engine
engine_args = {}
if not DATABASE_URL.startswith("sqlite"):
    engine_args["pool_pre_ping"] = True
engine = create_engine(DATABASE_URL, **engine_args)

def reset_database():
    """Drop all tables and prepare for re-initialization with UUID schema."""
    
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        inspector = inspect(engine)
        
        # Get all table names
        tables = inspector.get_table_names()
        logging.info(f"Found tables: {tables}")
        
        try:
            # Disable foreign key constraints temporarily
            conn.execute(text("SET session_replication_role = 'replica';"))
            logging.info("Disabled foreign key constraints")
            
            # Drop all tables
            for table in tables:
                logging.info(f"Dropping table: {table}")
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
            
            # Re-enable foreign key constraints
            conn.execute(text("SET session_replication_role = 'origin';"))
            logging.info("Re-enabled foreign key constraints")
            
            logging.info("Database reset complete!")
            logging.info("You can now run your application to re-initialize the database with UUID schema.")
            
        except Exception as e:
            logging.error(f"Error resetting database: {e}")
            raise

if __name__ == "__main__":
    reset_database()
