class SupplierAgentError(Exception):
    """Base exception for all supplier agent related errors."""
    pass

class AgentCreationError(SupplierAgentError):
    """Raised when there is an error creating a supplier agent."""
    pass

class AgentNotFoundError(SupplierAgentError):
    """Raised when a requested agent is not found."""
    pass

class DuplicateAgentError(SupplierAgentError):
    """Raised when attempting to create an agent with a name that already exists."""
    pass

class InvalidAgentTypeError(SupplierAgentError):
    """Raised when an invalid agent type is specified."""
    pass

class AgentOperationError(SupplierAgentError):
    """Raised when there is an error during agent operations."""
    pass 