import pytest
import logging
from unittest.mock import Mock, patch
from src.agents.supplier_agent_factory import SupplierAgentFactory
from src.agents.exceptions import (
    AgentCreationError,
    AgentNotFoundError,
    DuplicateAgentError,
    InvalidAgentTypeError,
    AgentOperationError
)

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def factory():
    """Create a fresh factory instance for each test."""
    factory = SupplierAgentFactory()
    factory.clear_agents()
    return factory

class TestSupplierAgentIntegration:
    """Integration tests for the supplier agent system."""
    
    def test_coordinator_regional_agent_interaction(self, factory):
        """Test interaction between coordinator and regional agents."""
        # Create all agents
        agents = factory.create_all_agents()
        coordinator = agents['coordinator']
        county_agent = agents['county']
        state_agent = agents['state']
        
        # Test coordination between agents
        assert coordinator.name == 'SupplierCoordinator'
        assert county_agent.name == 'CountySupplier'
        assert state_agent.name == 'StateSupplier'
        
        # Verify agent hierarchy
        assert coordinator in factory.get_all_agents().values()
        assert county_agent in factory.get_all_agents().values()
        assert state_agent in factory.get_all_agents().values()
    
    def test_regional_agent_operations(self, factory):
        """Test operations across different regional agents."""
        # Create regional agents
        county_agent = factory.create_agent('county', 'TestCounty')
        state_agent = factory.create_agent('state', 'TestState')
        national_agent = factory.create_agent('national', 'TestNational')
        
        # Test agent operations
        assert county_agent.name == 'TestCounty'
        assert state_agent.name == 'TestState'
        assert national_agent.name == 'TestNational'
        
        # Verify agent persistence
        assert factory.get_agent('TestCounty') == county_agent
        assert factory.get_agent('TestState') == state_agent
        assert factory.get_agent('TestNational') == national_agent
    
    def test_error_handling_and_recovery(self, factory):
        """Test error handling and recovery across the system."""
        # Test invalid agent creation
        with pytest.raises(InvalidAgentTypeError):
            factory.create_agent('invalid_type', 'TestAgent')
        
        # Test duplicate agent creation
        factory.create_agent('county', 'TestAgent')
        with pytest.raises(DuplicateAgentError):
            factory.create_agent('state', 'TestAgent')
        
        # Test agent removal and recreation
        factory.remove_agent('TestAgent')
        new_agent = factory.create_agent('county', 'TestAgent')
        assert new_agent is not None
        assert new_agent.name == 'TestAgent'
    
    def test_concurrent_operations(self, factory):
        """Test concurrent operations across the system."""
        import threading
        import time
        
        def create_and_remove_agents():
            for i in range(5):
                agent_name = f'TestAgent{i}'
                factory.create_agent('county', agent_name)
                time.sleep(0.1)  # Simulate some work
                factory.remove_agent(agent_name)
        
        # Create multiple threads
        threads = [threading.Thread(target=create_and_remove_agents) for _ in range(3)]
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify system state
        assert len(factory.get_all_agents()) == 0
    
    def test_agent_lifecycle(self, factory):
        """Test complete agent lifecycle."""
        # Create agent
        agent = factory.create_agent('county', 'TestAgent')
        assert agent is not None
        
        # Verify agent exists
        assert factory.get_agent('TestAgent') == agent
        
        # Remove agent
        assert factory.remove_agent('TestAgent') is True
        
        # Verify agent is removed
        with pytest.raises(AgentNotFoundError):
            factory.get_agent('TestAgent')
        
        # Clear all agents
        factory.clear_agents()
        assert len(factory.get_all_agents()) == 0
    
    @patch('src.agents.supplier_agent_factory.logger')
    def test_logging_integration(self, mock_logger, factory):
        """Test logging integration across the system."""
        # Create an agent
        factory.create_agent('county', 'TestAgent')
        
        # Verify logging calls
        mock_logger.info.assert_called()
        mock_logger.error.assert_not_called()
        
        # Test error logging
        with pytest.raises(InvalidAgentTypeError):
            factory.create_agent('invalid_type', 'TestAgent')
        
        mock_logger.error.assert_called()
    
    def test_factory_singleton_consistency(self):
        """Test factory singleton pattern across multiple instances."""
        factory1 = SupplierAgentFactory()
        factory2 = SupplierAgentFactory()
        
        # Create agent in first instance
        agent1 = factory1.create_agent('county', 'TestAgent')
        
        # Verify agent exists in second instance
        agent2 = factory2.get_agent('TestAgent')
        assert agent1 == agent2
        
        # Clear agents in first instance
        factory1.clear_agents()
        
        # Verify agents are cleared in second instance
        with pytest.raises(AgentNotFoundError):
            factory2.get_agent('TestAgent') 