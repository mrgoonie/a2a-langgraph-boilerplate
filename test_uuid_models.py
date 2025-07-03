#!/usr/bin/env python3
"""
Test script to verify that UUID-based models are working correctly.
This script will:
1. Create a new MCP server
2. Create a new Crew
3. Create a new Tool (linked to the MCP server)
4. Create a new Agent (linked to the Crew)
5. Link the Tool to the Agent
6. Create a new Conversation
7. Retrieve all created entities and verify the relationships
"""

import os
import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.base import Base
from app.models.mcp_server import McpServer
from app.models.crew import Crew
from app.models.agent import Agent
from app.models.tool import Tool
from app.models.conversation import Conversation
from app.models.agent_tool import agent_tool
import uuid

# Load environment variables
load_dotenv()

def test_uuid_models():
    """Test UUID-based models by creating and retrieving records."""
    # Create a session
    db = SessionLocal()
    
    try:
        print("Testing UUID-based models...")
        
        # Create a new MCP server with unique URL (using timestamp)
        print("Creating MCP server...")
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        unique_url = f"http://test-mcp-server-{timestamp}.local"
        mcp_server = McpServer(name="Test MCP Server", url=unique_url)
        db.add(mcp_server)
        db.flush()  # Flush to get the UUID
        mcp_server_id = mcp_server.id
        print(f"Created MCP server with ID: {mcp_server_id}")
        
        # Create a new Crew
        print("Creating Crew...")
        crew = Crew(name="Test Crew")
        db.add(crew)
        db.flush()
        crew_id = crew.id
        print(f"Created Crew with ID: {crew_id}")
        
        # Create a new Tool linked to the MCP server
        print("Creating Tool...")
        tool = Tool(name="Test Tool", description="A test tool", mcp_server_id=mcp_server_id)
        db.add(tool)
        db.flush()
        tool_id = tool.id
        print(f"Created Tool with ID: {tool_id}")
        
        # Create a new Agent linked to the Crew
        print("Creating Agent...")
        agent = Agent(
            name="Test Agent",
            crew_id=crew_id,
            role="tester",
            system_prompt="You are a test agent."
        )
        db.add(agent)
        db.flush()
        agent_id = agent.id
        print(f"Created Agent with ID: {agent_id}")
        
        # Link the Tool to the Agent
        print("Linking Tool to Agent...")
        db.execute(
            agent_tool.insert().values(
                agent_id=agent_id,
                tool_id=tool_id
            )
        )

        # Create a new Conversation linked to the Crew and Agent
        print("Creating Conversation...")
        conversation = Conversation(
            user_input="Hello test agent",
            agent_output="Hello user",
            crew_id=crew_id,
            agent_id=agent_id
        )
        db.add(conversation)
        db.flush()
        conversation_id = conversation.id
        print(f"Created Conversation with ID: {conversation_id}")
        
        # Commit all changes
        db.commit()
        print("All records committed to the database.")
        
        # Retrieve and verify the records
        print("\nVerifying records...")
        
        # Retrieve the MCP server
        retrieved_mcp_server = db.query(McpServer).filter(McpServer.id == mcp_server_id).first()
        print(f"Retrieved MCP server: {retrieved_mcp_server.name} (ID: {retrieved_mcp_server.id})")
        
        # Retrieve the Crew
        retrieved_crew = db.query(Crew).filter(Crew.id == crew_id).first()
        print(f"Retrieved Crew: {retrieved_crew.name} (ID: {retrieved_crew.id})")
        
        # Retrieve the Tool
        retrieved_tool = db.query(Tool).filter(Tool.id == tool_id).first()
        print(f"Retrieved Tool: {retrieved_tool.name} (ID: {retrieved_tool.id})")
        print(f"Tool's MCP server ID: {retrieved_tool.mcp_server_id}")
        
        # Retrieve the Agent
        retrieved_agent = db.query(Agent).filter(Agent.id == agent_id).first()
        print(f"Retrieved Agent: {retrieved_agent.name} (ID: {retrieved_agent.id})")
        print(f"Agent's Crew ID: {retrieved_agent.crew_id}")

        # Retrieve the Conversation
        retrieved_conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        print(f"Retrieved Conversation: ID: {retrieved_conversation.id}")
        print(f"Conversation user input: {retrieved_conversation.user_input}")
        print(f"Conversation agent output: {retrieved_conversation.agent_output}")
        
        # Verify Tool-Agent relationship using relationship
        print("\nVerifying relationships...")
        print("Accessing relationship: Agent's tools:")
        for t in retrieved_agent.tools:
            print(f"- {t.name} (ID: {t.id})")
        
        # Verify Tool's MCP Server relationship
        print("\nAccessing relationship: Tool's MCP Server:")
        print(f"- {retrieved_tool.mcp_server.name} (ID: {retrieved_tool.mcp_server.id})")

        # Verify Agent's Crew relationship
        print("\nAccessing relationship: Agent's Crew:")
        print(f"- {retrieved_agent.crew.name} (ID: {retrieved_agent.crew.id})")

        # Verify Crew's Agents relationship
        print("\nAccessing relationship: Crew's Agents:")
        for a in retrieved_crew.agents:
            print(f"- {a.name} (ID: {a.id})")

        # Verify Conversation relationships
        print("\nAccessing relationship: Conversation's Agent:")
        print(f"- {retrieved_conversation.agent.name} (ID: {retrieved_conversation.agent.id})")

        print("\nAccessing relationship: Conversation's Crew:")
        print(f"- {retrieved_conversation.crew.name} (ID: {retrieved_conversation.crew.id})")

        # Verify all relationships
        print("\nVerification completed successfully!")
        print("All UUID-based models and relationships are working correctly.")
        
    except Exception as e:
        db.rollback()
        print(f"Error during testing: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_uuid_models()
