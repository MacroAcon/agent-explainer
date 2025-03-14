import pytest
from unittest.mock import Mock, patch
from src.agents.supplier_agent_factory import SupplierAgentFactory
from src.agents.exceptions import (
    AgentCreationError,
    AgentNotFoundError,
    DuplicateAgentError,
    InvalidAgentTypeError,
    AgentOperationError
)

@pytest.fixture
def factory():
    """Create a fresh factory instance for each test."""
    factory = SupplierAgentFactory()
    factory.clear_agents()
    return factory

def test_singleton_pattern():
    """Test that the factory follows the singleton pattern."""
    factory1 = SupplierAgentFactory()
    factory2 = SupplierAgentFactory()
    assert factory1 is factory2

def test_create_agent(factory):
    """Test creating a single agent."""
    agent = factory.create_agent('county', 'TestCounty')
    assert agent is not None
    assert agent.name == 'TestCounty'
    assert factory.get_agent('TestCounty') == agent

def test_create_agent_invalid_type(factory):
    """Test creating an agent with invalid type."""
    with pytest.raises(InvalidAgentTypeError):
        factory.create_agent('invalid_type', 'TestAgent')

def test_create_agent_duplicate_name(factory):
    """Test creating an agent with duplicate name."""
    factory.create_agent('county', 'TestAgent')
    with pytest.raises(DuplicateAgentError):
        factory.create_agent('state', 'TestAgent')

def test_get_agent_not_found(factory):
    """Test getting a non-existent agent."""
    with pytest.raises(AgentNotFoundError):
        factory.get_agent('NonExistentAgent')

def test_create_all_agents(factory):
    """Test creating all agents."""
    agents = factory.create_all_agents()
    assert len(agents) == 5
    assert 'coordinator' in agents
    assert 'county' in agents
    assert 'state' in agents
    assert 'national' in agents
    assert 'international' in agents

def test_remove_agent(factory):
    """Test removing an agent."""
    factory.create_agent('county', 'TestAgent')
    assert factory.remove_agent('TestAgent') is True
    with pytest.raises(AgentNotFoundError):
        factory.get_agent('TestAgent')

def test_remove_nonexistent_agent(factory):
    """Test removing a non-existent agent."""
    assert factory.remove_agent('NonExistentAgent') is False

def test_clear_agents(factory):
    """Test clearing all agents."""
    factory.create_agent('county', 'TestAgent1')
    factory.create_agent('state', 'TestAgent2')
    factory.clear_agents()
    assert len(factory.get_all_agents()) == 0

def test_get_all_agents(factory):
    """Test getting all agents."""
    factory.create_agent('county', 'TestAgent1')
    factory.create_agent('state', 'TestAgent2')
    agents = factory.get_all_agents()
    assert len(agents) == 2
    assert 'TestAgent1' in agents
    assert 'TestAgent2' in agents

@patch('src.agents.supplier_agent_factory.CountySupplierAgent')
def test_agent_creation_error(mock_county_agent, factory):
    """Test handling of agent creation errors."""
    mock_county_agent.side_effect = Exception("Creation failed")
    with pytest.raises(AgentCreationError):
        factory.create_agent('county', 'TestAgent')

def test_thread_safety(factory):
    """Test thread safety of the factory."""
    import threading
    import time
    
    def create_agents():
        for i in range(10):
            factory.create_agent('county', f'TestAgent{i}')
    
    threads = [threading.Thread(target=create_agents) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    
    agents = factory.get_all_agents()
    assert len(agents) == 50  # 10 agents * 5 threads 