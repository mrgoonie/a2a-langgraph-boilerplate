# Testing Guide

This guide covers the testing approach and test suite for the A2A LangGraph Boilerplate project.

## Test Structure

The project uses pytest for testing with the following structure:

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_agents.py           # Agent API tests
├── test_crews.py            # Crew API tests
├── test_conversations.py    # Conversation API tests
├── test_mcp_servers.py      # MCP Server API tests
├── test_tools.py            # Tool API tests
├── test_ai_crew_chat.py     # AI crew chat workflow tests
├── test_ai_crew_simple_demo.py  # Complete workflow demonstration
└── test_readme_workflow.py  # README workflow examples
```

## Test Configuration

### Test Database Setup

The test suite uses an in-memory SQLite database for fast, isolated testing:

```python
# conftest.py
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
```

### Test Fixtures

Key fixtures available in all tests:

- `setup_database`: Creates database tables before tests
- `db_session`: Provides a database session for each test
- `client`: FastAPI test client with database dependency override

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Files

```bash
pytest tests/test_crews.py
pytest tests/test_agents.py
pytest tests/test_mcp_servers.py
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests with Coverage

```bash
pytest --cov=app
```

## Test Categories

### 1. API Endpoint Tests

These tests verify the CRUD operations for all API endpoints:

#### Crew Tests (`test_crews.py`)
- Create crew
- Read crews (list all)
- Read crew (get by ID)
- Update crew
- Delete crew

#### Agent Tests (`test_agents.py`)
- Create agent
- Read agents (list all)
- Read agent (get by ID)
- Update agent
- Delete agent
- Add tool to agent

#### MCP Server Tests (`test_mcp_servers.py`)
- Create MCP server
- Read MCP servers
- Read MCP server by ID
- Update MCP server
- Delete MCP server

#### Tool Tests (`test_tools.py`)
- Create tool
- Read tools
- Read tool by ID
- Update tool
- Delete tool

#### Conversation Tests (`test_conversations.py`)
- Create conversation
- Read conversations
- Read conversation by ID

### 2. Integration Tests

#### AI Crew Chat Tests (`test_ai_crew_chat.py`)
Tests the complete AI crew workflow with agent interactions.

#### AI Crew Simple Demo (`test_ai_crew_simple_demo.py`)
Comprehensive demonstration of the complete workflow:
- Creates crew with supervisor agent
- Adds specialized agents (Researcher, Coder, Summarizer)
- Configures MCP servers and tools
- Executes prompts through the crew
- Validates workflow execution

#### README Workflow Tests (`test_readme_workflow.py`)
Tests the examples shown in the README to ensure they work correctly.

## Test Examples

### Basic API Test Example

```python
def test_create_crew(client: TestClient, db_session: Session):
    response = client.post("/crews/", json={"name": "Test Crew"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Crew"
    assert "id" in data
```

### Integration Test Example

```python
def test_complete_workflow(client: TestClient, db_session: Session):
    # Create crew
    crew_response = client.post("/crews/", json={
        "name": "Research Team",
        "description": "A team for research tasks"
    })
    crew_id = crew_response.json()["id"]
    
    # Create agent
    agent_response = client.post("/agents/", json={
        "name": "Researcher",
        "role": "researcher",
        "crew_id": crew_id
    })
    agent_id = agent_response.json()["id"]
    
    # Verify workflow
    assert crew_response.status_code == 200
    assert agent_response.status_code == 200
```

## Test Database

### In-Memory Database

Tests use SQLite in-memory database for:
- Fast test execution
- Isolated test environment
- No external dependencies
- Automatic cleanup

### Database Schema

The test database uses the same schema as production:
- All tables are created from SQLAlchemy models
- Foreign key relationships are maintained
- UUID primary keys are supported

## Mocking and External Dependencies

### MCP Server Testing

For MCP server integration tests:
- Uses real MCP server URLs where possible
- Handles authentication gracefully
- Provides meaningful error messages for missing credentials

### API Client Testing

- Uses FastAPI TestClient for HTTP requests
- Dependency injection for database sessions
- Proper setup and teardown for each test

## Test Data Management

### Test Isolation

Each test runs in its own transaction:
- Database changes are rolled back after each test
- No test data pollution between tests
- Clean state for every test

### Test Data Creation

Tests create their own test data:
- Minimal data creation for each test
- Focused on testing specific functionality
- Clear and predictable test scenarios

## Running Tests in Development

### Watch Mode

For continuous testing during development:

```bash
pytest --watch
```

### Specific Test Patterns

```bash
# Run tests matching a pattern
pytest -k "test_crew"

# Run tests in a specific file
pytest tests/test_crews.py::test_create_crew

# Run tests with specific markers
pytest -m "integration"
```

## Test Performance

### Fast Test Execution

- In-memory database for speed
- Minimal test data creation
- Efficient test isolation
- Parallel test execution support

### Test Optimization

- Shared fixtures where appropriate
- Efficient database operations
- Minimal external API calls
- Fast assertion strategies

## Debugging Tests

### Test Failures

When tests fail:
1. Check the error message and traceback
2. Verify test data setup
3. Check database state
4. Examine API response details

### Debugging Tools

```bash
# Run with debug output
pytest -v -s

# Run single test for debugging
pytest tests/test_crews.py::test_create_crew -v -s

# Use pdb for debugging
pytest --pdb
```

## Test Coverage

### Coverage Reports

Generate coverage reports:

```bash
pytest --cov=app --cov-report=html
```

### Coverage Goals

- Aim for high coverage of core functionality
- Focus on critical business logic
- Test error handling paths
- Cover edge cases and boundary conditions

## Continuous Integration

### GitHub Actions

Tests run automatically on:
- Pull requests
- Push to main branch
- Scheduled runs

### Test Environment

CI environment:
- Uses PostgreSQL for integration tests
- Runs full test suite
- Generates coverage reports
- Validates all dependencies

## Best Practices

### Test Organization

- Group related tests in the same file
- Use descriptive test names
- Keep tests focused and atomic
- Use fixtures for common setup

### Test Quality

- Test both success and failure scenarios
- Verify error handling
- Check edge cases
- Validate data integrity

### Test Maintenance

- Keep tests updated with code changes
- Remove obsolete tests
- Refactor duplicate test code
- Document complex test scenarios