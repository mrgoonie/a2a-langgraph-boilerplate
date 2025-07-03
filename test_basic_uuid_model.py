#!/usr/bin/env python3
"""
Simple test script to verify that a single UUID-based model works correctly.
This script will:
1. Create a new MCP server
2. Retrieve the created MCP server by UUID
"""

import os
import random
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.mcp_server import McpServer
import uuid

# Load environment variables
load_dotenv()

def test_uuid_model():
    """Test a single UUID-based model by creating and retrieving a record."""
    # Create a session
    db = SessionLocal()
    
    try:
        print("Testing basic UUID-based model...")
        
        # Create a new MCP server with a unique URL to avoid unique constraint violation
        print("Creating MCP server...")
        unique_port = random.randint(8000, 9999)
        unique_url = f"http://localhost:{unique_port}"
        mcp_server = McpServer(name="Test MCP Server", url=unique_url)
        db.add(mcp_server)
        db.flush()  # Flush to get the UUID
        mcp_server_id = mcp_server.id
        print(f"Created MCP server with ID: {mcp_server_id}")
        
        # Commit the changes
        db.commit()
        print("Record committed to the database.")
        
        # Retrieve and verify the record
        print("\nVerifying record...")
        
        # Retrieve the MCP server
        retrieved_mcp_server = db.query(McpServer).filter(McpServer.id == mcp_server_id).first()
        print(f"Retrieved MCP server: {retrieved_mcp_server.name} (ID: {retrieved_mcp_server.id})")
        
        # Verify equality of UUIDs
        print(f"\nVerifying UUID equivalence...")
        print(f"Original UUID: {mcp_server_id}")
        print(f"Retrieved UUID: {retrieved_mcp_server.id}")
        print(f"UUIDs match: {mcp_server_id == retrieved_mcp_server.id}")
        
        print("\nVerification completed successfully!")
        print("Basic UUID-based model is working correctly.")
        
    except Exception as e:
        db.rollback()
        print(f"Error during testing: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_uuid_model()
