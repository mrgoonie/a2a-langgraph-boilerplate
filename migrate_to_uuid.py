import uuid
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Table, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func

from app.models.base import Base, GUID, generate_uuid

# Explicitly set the database connection string
DATABASE_URL = "postgresql://postgres:postgresql@127.0.0.1:5432/a2a-langgraph-boilerplate"

# Enable logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("migration.log"),
        logging.StreamHandler()
    ]
)

# Create engine and session
engine_args = {}
if not DATABASE_URL.startswith("sqlite"):
    engine_args["pool_size"] = 100
    engine_args["pool_timeout"] = 30

engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a temporary metadata for old schema
old_metadata = MetaData()

# Define old schema (integer-based) tables for reference
old_crews = Table(
    "crews", 
    old_metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("created_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True))
)

old_agents = Table(
    "agents", 
    old_metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("role", String),
    Column("system_prompt", Text),
    Column("crew_id", Integer, ForeignKey("crews.id")),
    Column("created_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True))
)

old_mcp_servers = Table(
    "mcp_servers", 
    old_metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("url", String),
    Column("created_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True))
)

old_tools = Table(
    "tools", 
    old_metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("description", String),
    Column("mcp_server_id", Integer, ForeignKey("mcp_servers.id")),
    Column("created_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True))
)

old_agent_tool = Table(
    "agent_tool", 
    old_metadata,
    Column("agent_id", Integer, ForeignKey("agents.id"), primary_key=True),
    Column("tool_id", Integer, ForeignKey("tools.id"), primary_key=True)
)

old_conversations = Table(
    "conversations", 
    old_metadata,
    Column("id", Integer, primary_key=True),
    Column("crew_id", Integer, ForeignKey("crews.id")),
    Column("agent_id", Integer, ForeignKey("agents.id")),
    Column("user_input", Text),
    Column("agent_output", Text),
    Column("created_at", DateTime(timezone=True))
)

# Migration mappings to track old ID to new UUID
id_mappings = {
    "crews": {},
    "agents": {},
    "mcp_servers": {},
    "tools": {},
    "conversations": {}
}

def migrate_data():
    logging.info("Starting migration from integer IDs to UUIDs...")
    # Create a connection and reflect existing tables
    with engine.connect() as conn:
        conn.execution_options(isolation_level="SERIALIZABLE")
        old_metadata.reflect(bind=engine)
        
        # Create session
        session = SessionLocal()
        
        try:
            print("Starting migration from integer IDs to UUIDs...")
            
            # Step 1: Create temporary tables with UUID schema (adding _new suffix)
            # We'll import all models which now have UUID schema
            from app.models.crew import Crew
            from app.models.agent import Agent
            from app.models.mcp_server import McpServer
            from app.models.tool import Tool
            from app.models.conversation import Conversation
            from app.models.agent_tool import agent_tool
            
            # Create new schema tables with temp names
            new_metadata = MetaData()
            
            # Create new tables with UUID-based schema
            crew_new = Table(
                "crews_new", 
                new_metadata,
                Column("id", GUID, primary_key=True, default=generate_uuid),
                Column("name", String),
                Column("created_at", DateTime(timezone=True)),
                Column("updated_at", DateTime(timezone=True))
            )
            
            agent_new = Table(
                "agents_new", 
                new_metadata,
                Column("id", GUID, primary_key=True, default=generate_uuid),
                Column("name", String),
                Column("role", String),
                Column("system_prompt", Text),
                Column("crew_id", GUID, ForeignKey("crews_new.id")),
                Column("created_at", DateTime(timezone=True)),
                Column("updated_at", DateTime(timezone=True))
            )
            
            mcp_server_new = Table(
                "mcp_servers_new", 
                new_metadata,
                Column("id", GUID, primary_key=True, default=generate_uuid),
                Column("name", String),
                Column("url", String),
                Column("created_at", DateTime(timezone=True)),
                Column("updated_at", DateTime(timezone=True))
            )
            
            tool_new = Table(
                "tools_new", 
                new_metadata,
                Column("id", GUID, primary_key=True, default=generate_uuid),
                Column("name", String),
                Column("description", String),
                Column("mcp_server_id", GUID, ForeignKey("mcp_servers_new.id")),
                Column("created_at", DateTime(timezone=True)),
                Column("updated_at", DateTime(timezone=True))
            )
            
            conversation_new = Table(
                "conversations_new", 
                new_metadata,
                Column("id", GUID, primary_key=True, default=generate_uuid),
                Column("crew_id", GUID, ForeignKey("crews_new.id")),
                Column("agent_id", GUID, ForeignKey("agents_new.id")),
                Column("user_input", Text),
                Column("agent_output", Text),
                Column("created_at", DateTime(timezone=True))
            )
            
            # Handle the agent_tool association table
            agent_tool_new = Table(
                "agent_tool_new",
                new_metadata,
                Column("agent_id", GUID, ForeignKey("agents_new.id"), primary_key=True),
                Column("tool_id", GUID, ForeignKey("tools_new.id"), primary_key=True)
            )
            
            # Create new tables
            new_metadata.create_all(bind=engine)
            logging.info("Created new tables with UUID schema")
            
            # Step 2: Migrate data from old tables to new tables
            # Helper function to check if table exists
            def table_exists(table_name):
                query = text("""SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = :table_name
                )""")
                exists = conn.execute(query, {"table_name": table_name}).scalar()
                logging.debug(f"Table {table_name} exists: {exists}")
                return exists
                
            logging.info("Migrating crews...")
            # Migrate crews first (no foreign key dependencies)
            if table_exists('crews'):
                for crew in conn.execute(old_crews.select()).fetchall():
                    new_uuid = uuid.uuid4()
                    id_mappings["crews"][crew.id] = new_uuid
                    conn.execute(
                        Table("crews_new", new_metadata).insert().values(
                            id=new_uuid,
                            name=crew.name,
                            created_at=crew.created_at,
                            updated_at=crew.updated_at
                        )
                    )
                
            logging.info("Migrating mcp_servers...")
            # Migrate mcp_servers (no foreign key dependencies)
            if table_exists('mcp_servers'):
                for server in conn.execute(old_mcp_servers.select()).fetchall():
                    new_uuid = uuid.uuid4()
                    id_mappings["mcp_servers"][server.id] = new_uuid
                    conn.execute(
                        Table("mcp_servers_new", new_metadata).insert().values(
                            id=new_uuid,
                            name=server.name,
                            url=server.url,
                            created_at=server.created_at,
                            updated_at=server.updated_at
                        )
                    )
            
            logging.info("Migrating agents...")
            # Migrate agents (depends on crews)
            if table_exists('agents'):
                for agent in conn.execute(old_agents.select()).fetchall():
                    new_uuid = uuid.uuid4()
                    id_mappings["agents"][agent.id] = new_uuid
                    
                    # Get the new crew UUID
                    new_crew_id = id_mappings["crews"].get(agent.crew_id)
                    
                    conn.execute(
                        Table("agents_new", new_metadata).insert().values(
                            id=new_uuid,
                            name=agent.name,
                            role=agent.role,
                            system_prompt=agent.system_prompt,
                            crew_id=new_crew_id,
                            created_at=agent.created_at,
                            updated_at=agent.updated_at
                        )
                    )
            
            logging.info("Migrating tools...")
            # Migrate tools (depends on mcp_servers)
            if table_exists('tools'):
                for tool in conn.execute(old_tools.select()).fetchall():
                    new_uuid = uuid.uuid4()
                    id_mappings["tools"][tool.id] = new_uuid
                    
                    # Get the new mcp_server UUID
                    new_mcp_server_id = id_mappings["mcp_servers"].get(tool.mcp_server_id)
                    
                    conn.execute(
                        Table("tools_new", new_metadata).insert().values(
                            id=new_uuid,
                            name=tool.name,
                            description=tool.description,
                            mcp_server_id=new_mcp_server_id,
                            created_at=tool.created_at,
                            updated_at=tool.updated_at
                        )
                    )
            
            logging.info("Migrating conversations...")
            # Migrate conversations (depends on crews and agents)
            if table_exists('conversations'):
                for conv in conn.execute(old_conversations.select()).fetchall():
                    new_uuid = uuid.uuid4()
                    id_mappings["conversations"][conv.id] = new_uuid
                    
                    # Get new crew and agent UUIDs
                    new_crew_id = id_mappings["crews"].get(conv.crew_id)
                    new_agent_id = id_mappings["agents"].get(conv.agent_id)
                    
                    conn.execute(
                        Table("conversations_new", new_metadata).insert().values(
                            id=new_uuid,
                            crew_id=new_crew_id,
                            agent_id=new_agent_id,
                            user_input=conv.user_input,
                            agent_output=conv.agent_output,
                            created_at=conv.created_at
                        )
                    )
            
            logging.info("Migrating agent_tool associations...")
            # Migrate agent_tool association table
            if table_exists('agent_tool'):
                for assoc in conn.execute(old_agent_tool.select()).fetchall():
                    new_agent_id = id_mappings["agents"].get(assoc.agent_id)
                    new_tool_id = id_mappings["tools"].get(assoc.tool_id)
                    
                    if new_agent_id and new_tool_id:
                        conn.execute(
                            agent_tool_new.insert().values(
                                agent_id=new_agent_id,
                                tool_id=new_tool_id
                            )
                        )
            
            # Commit the transaction to ensure all data is saved
            conn.commit()
            
            logging.info("Data migration completed successfully!")
            logging.info("===============================================")
            logging.info("IMPORTANT: The migration script has successfully created new tables with _new suffix")
            logging.info("containing all your data with UUID primary keys.")
            logging.info("")
            logging.info("To complete the migration, update your code to use the new tables with _new suffix,")
            logging.info("or manually run these SQL commands to drop old tables and rename new ones:")
            
            print("\nSQL commands to finalize migration (run manually):\n")
            print("-- 1. First disable the constraints")
            print("SET session_replication_role = 'replica';")
            print("\n-- 2. Drop old tables")
            print("DROP TABLE IF EXISTS agent_tool CASCADE;")
            print("DROP TABLE IF EXISTS agents CASCADE;")
            print("DROP TABLE IF EXISTS crews CASCADE;")
            print("DROP TABLE IF EXISTS mcp_servers CASCADE;")
            print("DROP TABLE IF EXISTS tools CASCADE;")
            print("DROP TABLE IF EXISTS conversations CASCADE;")
            print("\n-- 3. Rename new tables")
            print("ALTER TABLE crews_new RENAME TO crews;")
            print("ALTER TABLE agents_new RENAME TO agents;")
            print("ALTER TABLE mcp_servers_new RENAME TO mcp_servers;")
            print("ALTER TABLE tools_new RENAME TO tools;")
            print("ALTER TABLE conversations_new RENAME TO conversations;")
            print("ALTER TABLE agent_tool_new RENAME TO agent_tool;")
            print("\n-- 4. Re-enable constraints")
            print("SET session_replication_role = 'origin';")
            
            logging.info("Migration generated successfully!")
            
        except Exception as e:
            # Rollback in case of error
            session.rollback()
            logging.error(f"Error during migration: {e}")
            raise
        finally:
            session.close()

if __name__ == "__main__":
    migrate_data()
