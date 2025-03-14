from typing import Dict, List, Any, Optional, Union, Callable, TypeVar, Generic
import asyncio
import inspect
import json
import logging
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, create_model

# Setup logging
logger = logging.getLogger(__name__)

# Define tool categories for better organization
class ToolCategory(str, Enum):
    DATA_PROCESSING = "data_processing"
    COMMUNICATION = "communication"
    INTEGRATION = "integration"
    ANALYTICS = "analytics"
    SECURITY = "security"
    UTILITY = "utility"
    CUSTOM = "custom"

# Define tool execution status
class ToolExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

# Define tool parameter schema
class ToolParameter(BaseModel):
    name: str
    description: str
    type: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "required": self.required,
            "default": self.default,
            "enum": self.enum
        }

# Define tool execution result
class ToolExecutionResult(BaseModel):
    tool_name: str
    status: ToolExecutionStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Define tool interface
class Tool(BaseModel):
    name: str
    description: str
    category: ToolCategory = ToolCategory.UTILITY
    parameters: List[ToolParameter] = Field(default_factory=list)
    function: Optional[Callable] = None
    async_function: Optional[Callable] = None
    required_permissions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary for serialization"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "parameters": [p.to_dict() for p in self.parameters],
            "required_permissions": self.required_permissions,
            "metadata": self.metadata
        }
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters against schema"""
        validated = {}
        errors = []
        
        # Check for required parameters
        for param in self.parameters:
            if param.required and param.name not in parameters:
                if param.default is not None:
                    validated[param.name] = param.default
                else:
                    errors.append(f"Missing required parameter: {param.name}")
            elif param.name in parameters:
                value = parameters[param.name]
                
                # Type validation (simple)
                if param.type == "string" and not isinstance(value, str):
                    errors.append(f"Parameter {param.name} must be a string")
                elif param.type == "number" and not isinstance(value, (int, float)):
                    errors.append(f"Parameter {param.name} must be a number")
                elif param.type == "boolean" and not isinstance(value, bool):
                    errors.append(f"Parameter {param.name} must be a boolean")
                elif param.type == "array" and not isinstance(value, list):
                    errors.append(f"Parameter {param.name} must be an array")
                elif param.type == "object" and not isinstance(value, dict):
                    errors.append(f"Parameter {param.name} must be an object")
                
                # Enum validation
                if param.enum is not None and value not in param.enum:
                    errors.append(f"Parameter {param.name} must be one of: {param.enum}")
                
                validated[param.name] = value
        
        if errors:
            raise ValueError(f"Parameter validation errors: {', '.join(errors)}")
        
        return validated
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolExecutionResult:
        """Execute the tool with the given parameters"""
        start_time = datetime.now()
        
        try:
            # Validate parameters
            validated_params = self.validate_parameters(parameters)
            
            # Execute function
            if self.async_function:
                result = await self.async_function(**validated_params)
                status = ToolExecutionStatus.COMPLETED
                error = None
            elif self.function:
                result = self.function(**validated_params)
                status = ToolExecutionStatus.COMPLETED
                error = None
            else:
                raise ValueError(f"Tool {self.name} has no function implementation")
            
        except Exception as e:
            logger.exception(f"Error executing tool {self.name}")
            result = None
            status = ToolExecutionStatus.FAILED
            error = str(e)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return ToolExecutionResult(
            tool_name=self.name,
            status=status,
            result=result,
            error=error,
            execution_time=execution_time,
            metadata={"parameters": parameters}
        )

# Tool Registry for managing tools
class ToolRegistry:
    """Registry for managing and accessing tools"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.categories: Dict[ToolCategory, List[str]] = {category: [] for category in ToolCategory}
    
    def register_tool(self, tool: Tool) -> None:
        """Register a tool in the registry"""
        if tool.name in self.tools:
            logger.warning(f"Tool {tool.name} already registered, overwriting")
        
        self.tools[tool.name] = tool
        
        # Add to category index
        if tool.name not in self.categories[tool.category]:
            self.categories[tool.category].append(tool.name)
    
    def unregister_tool(self, tool_name: str) -> None:
        """Unregister a tool from the registry"""
        if tool_name in self.tools:
            tool = self.tools[tool_name]
            del self.tools[tool_name]
            
            # Remove from category index
            if tool_name in self.categories[tool.category]:
                self.categories[tool.category].remove(tool_name)
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(tool_name)
    
    def get_tools_by_category(self, category: ToolCategory) -> List[Tool]:
        """Get all tools in a category"""
        tool_names = self.categories.get(category, [])
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    def get_all_tools(self) -> List[Tool]:
        """Get all registered tools"""
        return list(self.tools.values())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert registry to dictionary for serialization"""
        return {
            "tools": {name: tool.to_dict() for name, tool in self.tools.items()},
            "categories": {category.value: tools for category, tools in self.categories.items()}
        }

# Tool decorator for easy tool creation
def tool(
    name: str,
    description: str,
    category: ToolCategory = ToolCategory.UTILITY,
    parameters: List[ToolParameter] = None,
    required_permissions: List[str] = None,
    metadata: Dict[str, Any] = None
):
    """Decorator to convert a function into a tool"""
    parameters = parameters or []
    required_permissions = required_permissions or []
    metadata = metadata or {}
    
    def decorator(func):
        # Determine if function is async
        is_async = asyncio.iscoroutinefunction(func)
        
        # If no parameters provided, infer from function signature
        if not parameters:
            sig = inspect.signature(func)
            inferred_parameters = []
            
            for param_name, param in sig.parameters.items():
                param_type = "string"  # Default type
                required = param.default == inspect.Parameter.empty
                default = None if required else param.default
                
                # Try to infer type from annotations
                if param.annotation != inspect.Parameter.empty:
                    if param.annotation == str:
                        param_type = "string"
                    elif param.annotation in (int, float):
                        param_type = "number"
                    elif param.annotation == bool:
                        param_type = "boolean"
                    elif param.annotation == list or getattr(param.annotation, "__origin__", None) == list:
                        param_type = "array"
                    elif param.annotation == dict or getattr(param.annotation, "__origin__", None) == dict:
                        param_type = "object"
                
                inferred_parameters.append(
                    ToolParameter(
                        name=param_name,
                        description=f"Parameter {param_name}",
                        type=param_type,
                        required=required,
                        default=default
                    )
                )
            
            parameters.extend(inferred_parameters)
        
        # Create tool
        tool = Tool(
            name=name,
            description=description,
            category=category,
            parameters=parameters,
            function=None if is_async else func,
            async_function=func if is_async else None,
            required_permissions=required_permissions,
            metadata=metadata
        )
        
        # Add tool attribute to function for easy access
        func.tool = tool
        
        return func
    
    return decorator

# Tool Chain for executing multiple tools in sequence
class ToolChain:
    """Chain of tools to be executed in sequence"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.steps: List[Dict[str, Any]] = []
    
    def add_step(
        self,
        tool_name: str,
        parameters: Dict[str, Any] = None,
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
        transform: Optional[Callable[[Any], Dict[str, Any]]] = None
    ) -> None:
        """Add a step to the chain"""
        parameters = parameters or {}
        
        self.steps.append({
            "tool_name": tool_name,
            "parameters": parameters,
            "condition": condition,
            "transform": transform
        })
    
    async def execute(
        self,
        tool_registry: ToolRegistry,
        initial_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute the chain of tools"""
        context = initial_context or {}
        results = []
        
        for i, step in enumerate(self.steps):
            # Check condition
            if step["condition"] and not step["condition"](context):
                logger.info(f"Skipping step {i+1} ({step['tool_name']}) due to condition")
                continue
            
            # Get tool
            tool = tool_registry.get_tool(step["tool_name"])
            if not tool:
                error = f"Tool {step['tool_name']} not found in registry"
                logger.error(error)
                results.append({
                    "step": i+1,
                    "tool_name": step["tool_name"],
                    "status": ToolExecutionStatus.FAILED,
                    "error": error
                })
                continue
            
            # Prepare parameters
            try:
                # Evaluate parameter templates from context
                parameters = {}
                for key, value in step["parameters"].items():
                    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                        # Extract variable name
                        var_name = value[2:-1]
                        if var_name in context:
                            parameters[key] = context[var_name]
                        else:
                            raise ValueError(f"Context variable {var_name} not found")
                    else:
                        parameters[key] = value
            except Exception as e:
                error = f"Error preparing parameters for step {i+1} ({step['tool_name']}): {str(e)}"
                logger.error(error)
                results.append({
                    "step": i+1,
                    "tool_name": step["tool_name"],
                    "status": ToolExecutionStatus.FAILED,
                    "error": error
                })
                continue
            
            # Execute tool
            try:
                result = await tool.execute(parameters)
                
                # Transform result if needed
                if step["transform"] and result.status == ToolExecutionStatus.COMPLETED:
                    try:
                        transformed = step["transform"](result.result)
                        context.update(transformed)
                    except Exception as e:
                        logger.error(f"Error transforming result for step {i+1} ({step['tool_name']}): {str(e)}")
                        result.error = f"Transform error: {str(e)}"
                        result.status = ToolExecutionStatus.FAILED
                elif result.status == ToolExecutionStatus.COMPLETED:
                    # Default behavior: add result to context with tool name as key
                    context[tool.name] = result.result
                
                results.append({
                    "step": i+1,
                    "tool_name": step["tool_name"],
                    "status": result.status,
                    "result": result.result if result.status == ToolExecutionStatus.COMPLETED else None,
                    "error": result.error,
                    "execution_time": result.execution_time
                })
            except Exception as e:
                error = f"Error executing step {i+1} ({step['tool_name']}): {str(e)}"
                logger.error(error)
                results.append({
                    "step": i+1,
                    "tool_name": step["tool_name"],
                    "status": ToolExecutionStatus.FAILED,
                    "error": error
                })
        
        return {
            "context": context,
            "results": results,
            "success": all(r["status"] == ToolExecutionStatus.COMPLETED for r in results)
        } 