#!/usr/bin/env python3
"""
Test for the agent model field feature.
This script demonstrates creating agents with and without custom OpenRouter models.
"""

import os
import sys
import uuid
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Add the project root to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import necessary modules from the project
from app.core.database import get_db, engine
from app.models.base import Base
from app.schemas.crew import CrewCreate
from app.schemas.agent import AgentCreate
from app.services import crew as crew_service
from app.services import agent as agent_service
from app.core.logging import get_logger

# Set up logging
logger = get_logger(__name__)

# Load environment variables
load_dotenv()

# Ensure database is set up
Base.metadata.create_all(bind=engine)

def test_agent_model_field():
    """
    Test the agent model field functionality by:
    1. Creating a crew
    2. Creating agents with and without custom models
    3. Verifying that the model field is correctly stored and retrieved
    """
    print("\n" + "=" * 80)
    print("TESTING AGENT MODEL FIELD")
    print("=" * 80)
    
    # Initialize database session
    db = next(get_db())
    
    try:
        # Step 1: Create a crew for testing
        print("\n[STEP 1] Creating test crew...")
        crew_data = CrewCreate(name="Model Field Test Crew")
        crew = crew_service.create_crew(db=db, crew=crew_data)
        print(f"Created test crew: {crew.name} (ID: {crew.id})")
        
        # Step 2: Create agents with and without custom model field
        print("\n[STEP 2] Creating agents with and without custom model field...")
        
        # Agent 1: Default agent with no custom model
        agent1_data = AgentCreate(
            name="Default Agent",
            crew_id=crew.id,
            role="assistant",
            system_prompt="You are a helpful assistant."
        )
        agent1 = agent_service.create_agent(db=db, agent=agent1_data)
        print(f"Created agent without custom model: {agent1.name} (ID: {agent1.id})")
        print(f"  Model value: {agent1.model if agent1.model else 'None (using default)'}")
        
        # Agent 2: Supervisor agent with custom model
        agent2_data = AgentCreate(
            name="Smart Supervisor",
            crew_id=crew.id,
            role="supervisor",
            system_prompt="You are a smart supervisor overseeing other agents.",
            model="anthropic/claude-3-opus-20240229"
        )
        agent2 = agent_service.create_agent(db=db, agent=agent2_data)
        print(f"Created supervisor with custom model: {agent2.name} (ID: {agent2.id})")
        print(f"  Model value: {agent2.model}")
        
        # Agent 3: Another agent with different custom model
        agent3_data = AgentCreate(
            name="Research Agent",
            crew_id=crew.id,
            role="researcher",
            system_prompt="You are a researcher focused on finding information.",
            model="anthropic/claude-3-sonnet-20240229"
        )
        agent3 = agent_service.create_agent(db=db, agent=agent3_data)
        print(f"Created researcher with custom model: {agent3.name} (ID: {agent3.id})")
        print(f"  Model value: {agent3.model}")
        
        # Step 3: Verify by retrieving agents from database
        print("\n[STEP 3] Verifying agents retrieved from database...")
        
        db_agent1 = agent_service.get_agent(db=db, agent_id=agent1.id)
        print(f"Retrieved agent 1: {db_agent1.name}")
        print(f"  Model value: {db_agent1.model if db_agent1.model else 'None (using default)'}")
        assert db_agent1.model is None, "Default agent should have None model value"
        
        db_agent2 = agent_service.get_agent(db=db, agent_id=agent2.id)
        print(f"Retrieved agent 2: {db_agent2.name}")
        print(f"  Model value: {db_agent2.model}")
        assert db_agent2.model == "anthropic/claude-3-opus-20240229", "Supervisor model value mismatch"
        
        db_agent3 = agent_service.get_agent(db=db, agent_id=agent3.id)
        print(f"Retrieved agent 3: {db_agent3.name}")
        print(f"  Model value: {db_agent3.model}")
        assert db_agent3.model == "anthropic/claude-3-sonnet-20240229", "Researcher model value mismatch"
        
        # Step 4: Test updating an agent's model
        print("\n[STEP 4] Testing agent model update...")
        updated_agent_data = AgentCreate(
            name="Default Agent Updated",
            crew_id=crew.id,
            role="assistant",
            system_prompt="You are a helpful assistant.",
            model="google/gemini-2.5-flash"  # Add a model to previously default agent
        )
        updated_agent = agent_service.update_agent(db=db, agent_id=agent1.id, agent=updated_agent_data)
        print(f"Updated agent 1: {updated_agent.name}")
        print(f"  New model value: {updated_agent.model}")
        assert updated_agent.model == "google/gemini-2.5-flash", "Updated model value mismatch"
        
        print("\n" + "=" * 80)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\nTest failed: {str(e)}")
        raise
    finally:
        # Clean up (optional - comment out if you want to keep the test data)
        if crew:
            crew_service.delete_crew(db=db, crew_id=crew.id)
            print("Cleanup: Deleted test crew and all associated agents")
        # Close the database session
        db.close()

if __name__ == "__main__":
    try:
        test_agent_model_field()
        print("All tests passed!")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        print(f"Test failed: {str(e)}")
