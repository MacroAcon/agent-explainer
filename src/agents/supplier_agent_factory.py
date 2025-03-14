from typing import Dict, Any, Optional
import logging
from threading import Lock
from .county_supplier_agent import CountySupplierAgent
from .state_supplier_agent import StateSupplierAgent
from .national_supplier_agent import NationalSupplierAgent
from .international_supplier_agent import InternationalSupplierAgent
from .supplier_coordinator_agent import SupplierCoordinatorAgent
from .exceptions import (
    AgentCreationError,
    AgentNotFoundError,
    DuplicateAgentError,
    InvalidAgentTypeError,
    AgentOperationError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupplierAgentFactory:
    """Factory class for creating and managing supplier agents at different regional levels."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """Implement singleton pattern with thread safety."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SupplierAgentFactory, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the factory if not already initialized."""
        if not hasattr(self, '_initialized'):
            self._agents: Dict[str, Any] = {}
            self._initialized = True
            logger.info("SupplierAgentFactory initialized")
    
    def create_agent(self, agent_type: str, name: Optional[str] = None) -> Any:
        """
        Create a supplier agent based on the specified type.
        
        Args:
            agent_type: Type of agent to create ('county', 'state', 'national', 'international', 'coordinator')
            name: Optional name for the agent. If not provided, a default name will be used.
            
        Returns:
            An instance of the requested supplier agent.
            
        Raises:
            InvalidAgentTypeError: If an invalid agent type is specified.
            DuplicateAgentError: If an agent with the same name already exists.
            AgentCreationError: If there is an error creating the agent.
        """
        try:
            agent_type = agent_type.lower()
            
            if agent_type not in ['county', 'state', 'national', 'international', 'coordinator']:
                raise InvalidAgentTypeError(f"Invalid agent type: {agent_type}")
            
            # Generate default name if not provided
            if name is None:
                name = f"{agent_type.capitalize()}Supplier"
            
            # Check if agent with same name exists
            if name in self._agents:
                raise DuplicateAgentError(f"Agent with name '{name}' already exists")
            
            # Create agent based on type
            with self._lock:
                try:
                    if agent_type == 'county':
                        agent = CountySupplierAgent(name=name)
                    elif agent_type == 'state':
                        agent = StateSupplierAgent(name=name)
                    elif agent_type == 'national':
                        agent = NationalSupplierAgent(name=name)
                    elif agent_type == 'international':
                        agent = InternationalSupplierAgent(name=name)
                    else:  # coordinator
                        agent = SupplierCoordinatorAgent(name=name)
                except Exception as e:
                    raise AgentCreationError(f"Failed to create {agent_type} agent: {str(e)}")
                
                # Store the agent instance
                self._agents[name] = agent
                logger.info(f"Created {agent_type} agent with name '{name}'")
                
                return agent
                
        except (InvalidAgentTypeError, DuplicateAgentError, AgentCreationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating agent: {str(e)}")
            raise AgentCreationError(f"Unexpected error creating agent: {str(e)}")
    
    def get_agent(self, name: str) -> Any:
        """
        Retrieve an existing agent by name.
        
        Args:
            name: Name of the agent to retrieve.
            
        Returns:
            The agent instance if found.
            
        Raises:
            AgentNotFoundError: If the agent is not found.
        """
        try:
            agent = self._agents.get(name)
            if agent:
                logger.debug(f"Retrieved agent with name '{name}'")
                return agent
            raise AgentNotFoundError(f"Agent with name '{name}' not found")
        except AgentNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving agent: {str(e)}")
            raise AgentOperationError(f"Error retrieving agent: {str(e)}")
    
    def create_all_agents(self) -> Dict[str, Any]:
        """
        Create all supplier agents with default names.
        
        Returns:
            Dictionary containing all created agents.
            
        Raises:
            AgentCreationError: If any agent creation fails.
        """
        try:
            agents = {}
            
            # Create coordinator first
            coordinator = self.create_agent('coordinator', 'SupplierCoordinator')
            agents['coordinator'] = coordinator
            
            # Create regional agents
            agents['county'] = self.create_agent('county', 'CountySupplier')
            agents['state'] = self.create_agent('state', 'StateSupplier')
            agents['national'] = self.create_agent('national', 'NationalSupplier')
            agents['international'] = self.create_agent('international', 'InternationalSupplier')
            
            logger.info("Successfully created all supplier agents")
            return agents
            
        except Exception as e:
            logger.error(f"Error creating all agents: {str(e)}")
            raise AgentCreationError(f"Failed to create all agents: {str(e)}")
    
    def get_all_agents(self) -> Dict[str, Any]:
        """
        Get all currently instantiated agents.
        
        Returns:
            Dictionary containing all agents.
            
        Raises:
            AgentOperationError: If there is an error retrieving agents.
        """
        try:
            return self._agents.copy()
        except Exception as e:
            logger.error(f"Error getting all agents: {str(e)}")
            raise AgentOperationError(f"Error getting all agents: {str(e)}")
    
    def clear_agents(self) -> None:
        """
        Clear all instantiated agents.
        
        Raises:
            AgentOperationError: If there is an error clearing agents.
        """
        try:
            with self._lock:
                self._agents.clear()
                logger.info("Cleared all supplier agents")
        except Exception as e:
            logger.error(f"Error clearing agents: {str(e)}")
            raise AgentOperationError(f"Error clearing agents: {str(e)}")
    
    def remove_agent(self, name: str) -> bool:
        """
        Remove a specific agent by name.
        
        Args:
            name: Name of the agent to remove.
            
        Returns:
            True if the agent was removed, False if it wasn't found.
            
        Raises:
            AgentOperationError: If there is an error removing the agent.
        """
        try:
            with self._lock:
                if name in self._agents:
                    del self._agents[name]
                    logger.info(f"Removed agent with name '{name}'")
                    return True
                logger.warning(f"Agent with name '{name}' not found for removal")
                return False
        except Exception as e:
            logger.error(f"Error removing agent: {str(e)}")
            raise AgentOperationError(f"Error removing agent: {str(e)}") 