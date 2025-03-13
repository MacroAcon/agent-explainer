from typing import List, Dict, Any, Optional, Set
from ag2 import CaptainAgent, SwarmAgent, UserProxyAgent, GroupChat, CommunicationChannel, TaskQueue
from .customer_service_agent import CustomerServiceAgent
from .appointment_scheduler_agent import AppointmentSchedulerAgent
from .medical_records_agent import MedicalRecordsAgent
from .billing_agent import BillingAgent
from .insurance_verification_agent import InsuranceVerificationAgent
from ..config.config import settings
from ..config.enhanced_settings import enhanced_settings
from .retail_operations_agent import RetailOperationsAgent
from .local_marketing_agent import LocalMarketingAgent
from .restaurant_operations_agent import RestaurantOperationsAgent
from .local_supplier_integration_agent import LocalSupplierIntegrationAgent
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict
import json

class BusinessSwarmCoordinator:
    """Coordinator for business automation agents with enhanced task management."""
    
    def __init__(self):
        # Define the captain's system message
        captain_message = """You are the captain of a business automation team focused on helping small businesses in Calhoun, GA succeed. Your team includes specialists in:
        1. Restaurant operations and kitchen management
        2. Retail operations and inventory management
        3. Local marketing and community engagement
        4. Local supplier and community integration
        5. Business analytics and optimization
        
        Your role is to:
        1. Understand business requests and delegate tasks to appropriate specialists
        2. Coordinate responses between different specialists
        3. Ensure all operations maintain customer privacy and data security
        4. Optimize business operations for the local Calhoun market
        5. Track and improve business performance metrics
        6. Maintain compliance with local regulations
        7. Foster strong community and supplier relationships
        """
        
        # Initialize communication channels with load balancing
        self.channels = {
            "operations": CommunicationChannel(
                name="operations",
                priority="high",
                participants=["RestaurantOps", "RetailOps"],
                routing_strategy="load_balanced",
                message_compression=True
            ),
            "marketing": CommunicationChannel(
                name="marketing",
                priority="medium",
                participants=["LocalMarketing", "CustomerService"],
                routing_strategy="load_balanced",
                message_compression=True
            ),
            "supply_chain": CommunicationChannel(
                name="supply_chain",
                priority="high",
                participants=["LocalSupplier", "RestaurantOps", "RetailOps"],
                routing_strategy="load_balanced",
                message_compression=True
            ),
            "customer_relations": CommunicationChannel(
                name="customer_relations",
                priority="medium",
                participants=["CustomerService", "LocalMarketing"],
                routing_strategy="load_balanced",
                message_compression=True
            )
        }
        
        # Initialize enhanced task queue with priority levels and dependency tracking
        self.task_queue = TaskQueue(
            max_concurrent=enhanced_settings.task.max_concurrent_tasks,
            priority_levels=enhanced_settings.task.priority_levels,
            dependency_tracking=True,
            retry_attempts=enhanced_settings.task.retry_attempts,
            retry_delay=enhanced_settings.task.retry_delay
        )
        
        # Initialize task batching
        self.task_batches = defaultdict(list)
        self.last_batch_process = datetime.now()
        
        # Initialize dependency graph
        self.dependency_graph = defaultdict(set)
        
        # Initialize specialized agents as SwarmAgents
        self.restaurant_ops_agent = SwarmAgent(
            name="RestaurantOps",
            agent_class=RestaurantOperationsAgent,
            system_message="Restaurant operations specialist for Calhoun, GA businesses.",
            channels=["operations", "supply_chain"]
        )
        
        self.retail_ops_agent = SwarmAgent(
            name="RetailOps",
            agent_class=RetailOperationsAgent,
            system_message="Retail operations specialist for Calhoun, GA businesses.",
            channels=["operations", "supply_chain"]
        )
        
        self.marketing_agent = SwarmAgent(
            name="LocalMarketing",
            agent_class=LocalMarketingAgent,
            system_message="Local marketing specialist for Calhoun, GA businesses.",
            channels=["marketing", "customer_relations"]
        )
        
        self.supplier_agent = SwarmAgent(
            name="LocalSupplier",
            agent_class=LocalSupplierIntegrationAgent,
            system_message="Local supplier integration specialist for Calhoun, GA businesses.",
            channels=["supply_chain"]
        )
        
        # Create the group chat with enhanced communication
        self.group_chat = GroupChat(
            agents=[
                self.restaurant_ops_agent,
                self.retail_ops_agent,
                self.marketing_agent,
                self.supplier_agent
            ],
            messages=[],
            channels=self.channels
        )
        
        # Initialize the captain agent with enhanced capabilities
        self.captain = CaptainAgent(
            name="BusinessCaptain",
            system_message=captain_message,
            group_chat=self.group_chat,
            task_queue=self.task_queue
        )
        
        # Register agents with the captain
        for agent in self.group_chat.agents:
            self.captain.register_agent(
                agent=agent,
                capabilities=self._get_agent_capabilities(agent)
            )
    
    def _get_agent_capabilities(self, agent: SwarmAgent) -> Dict[str, Any]:
        """Get detailed capabilities for an agent."""
        return {
            "tools": [tool["name"] for tool in agent.tools],
            "channels": agent.channels,
            "specialties": self._extract_specialties(agent.system_message),
            "memory_capacity": agent.long_term_memory.capacity
        }
    
    def _extract_specialties(self, system_message: str) -> List[str]:
        """Extract specialties from agent's system message."""
        specialties = []
        lines = system_message.split("\n")
        for line in lines:
            if line.strip().startswith(("1.", "2.", "3.", "4.", "5.")):
                specialty = line.split(".", 1)[1].strip()
                specialties.append(specialty)
        return specialties
    
    def _calculate_dynamic_priority(self, task: Dict[str, Any]) -> str:
        """Calculate dynamic priority based on task characteristics."""
        base_priority = task.get("priority", "medium")
        
        # Adjust priority based on dependencies
        if self.dependency_graph[task.get("id")]:
            base_priority = "high"
        
        # Adjust priority based on task age
        if "timestamp" in task:
            age = (datetime.now() - datetime.fromisoformat(task["timestamp"])).total_seconds()
            if age > enhanced_settings.task.task_timeout * 0.8:  # 80% of timeout
                base_priority = "high"
        
        # Adjust priority based on business impact
        if task.get("business_impact", 0) > 0.8:
            base_priority = "high"
        
        return base_priority
    
    def _extract_dependencies(self, task: Dict[str, Any]) -> Set[str]:
        """Extract task dependencies from task content and context."""
        dependencies = set()
        
        # Check for explicit dependencies in task
        if "dependencies" in task:
            dependencies.update(task["dependencies"])
        
        # Check for implicit dependencies in task content
        content = task.get("content", "").lower()
        if "after" in content or "following" in content or "depends on" in content:
            # Extract potential dependency IDs from content
            # This is a simple implementation - could be enhanced with NLP
            words = content.split()
            for i, word in enumerate(words):
                if word in ["after", "following", "depends"]:
                    if i + 1 < len(words):
                        dependencies.add(words[i + 1])
        
        return dependencies
    
    async def _process_batch(self, batch_key: str):
        """Process a batch of similar tasks."""
        if not self.task_batches[batch_key]:
            return
            
        batch = self.task_batches[batch_key]
        if len(batch) > enhanced_settings.performance.max_batch_size:
            batch = batch[:enhanced_settings.performance.max_batch_size]
        
        # Process batch in parallel
        tasks = [
            self._process_single_task(task)
            for task in batch
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Clear processed batch
        self.task_batches[batch_key] = []
        
        return results
    
    async def _process_single_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single task with dependency checking."""
        task_id = task.get("id")
        
        # Check dependencies
        if self.dependency_graph[task_id]:
            # Wait for dependencies to complete
            await self._wait_for_dependencies(task_id)
        
        # Process the task
        result = await self.captain.process_task(task)
        
        # Update dependency graph
        self._update_dependency_graph(task_id, result)
        
        return result
    
    async def _wait_for_dependencies(self, task_id: str):
        """Wait for task dependencies to complete."""
        while self.dependency_graph[task_id]:
            await asyncio.sleep(enhanced_settings.task.dependency_check_interval)
    
    def _update_dependency_graph(self, task_id: str, result: Dict[str, Any]):
        """Update the dependency graph after task completion."""
        # Remove this task from other tasks' dependencies
        for deps in self.dependency_graph.values():
            deps.discard(task_id)
        
        # Clear this task's dependencies
        self.dependency_graph[task_id].clear()
    
    async def process_task(
        self,
        task: str,
        context: Dict[str, Any] = None,
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """Process a business task with enhanced task management."""
        if context is None:
            context = {}
        
        # Add local business context
        context.update({
            "location": "Calhoun, GA",
            "business_type": context.get("business_type", "retail/restaurant"),
            "local_market": "small_business",
            "privacy_enabled": True,
            "timestamp": datetime.now().isoformat()
        })
        
        # Create a task message
        task_message = {
            "id": str(datetime.now().timestamp()),
            "content": task,
            "context": context,
            "timestamp": context["timestamp"],
            "priority": priority
        }
        
        # Extract dependencies
        dependencies = self._extract_dependencies(task_message)
        if dependencies:
            task_message["dependencies"] = list(dependencies)
            self.dependency_graph[task_message["id"]] = dependencies
        
        # Calculate dynamic priority
        task_message["priority"] = self._calculate_dynamic_priority(task_message)
        
        # Check if task can be batched
        if enhanced_settings.performance.batch_processing:
            batch_key = self._get_batch_key(task_message)
            if batch_key:
                self.task_batches[batch_key].append(task_message)
                
                # Process batch if it's full or enough time has passed
                now = datetime.now()
                if (len(self.task_batches[batch_key]) >= enhanced_settings.task.batch_size or
                    (now - self.last_batch_process).total_seconds() >= enhanced_settings.performance.min_batch_interval):
                    return await self._process_batch(batch_key)
        
        # Process single task if not batched
        return await self._process_single_task(task_message)
    
    def _get_batch_key(self, task: Dict[str, Any]) -> Optional[str]:
        """Determine if a task can be batched and return its batch key."""
        content = task.get("content", "").lower()
        
        # Define batchable task types
        batchable_types = {
            "inventory": ["stock", "inventory", "supply"],
            "marketing": ["promotion", "advertisement", "campaign"],
            "analytics": ["report", "analysis", "metrics"]
        }
        
        for batch_type, keywords in batchable_types.items():
            if any(keyword in content for keyword in keywords):
                return f"{batch_type}_{task.get('priority', 'medium')}"
        
        return None
    
    async def get_task_status(self) -> Dict[str, Any]:
        """Get the current status of tasks in the swarm."""
        return {
            "queue_status": await self.task_queue.get_status(),
            "agent_status": await self.captain.get_status(),
            "channel_status": {
                name: channel.get_status()
                for name, channel in self.channels.items()
            },
            "batch_status": {
                key: len(batch)
                for key, batch in self.task_batches.items()
            },
            "dependency_status": {
                task_id: len(deps)
                for task_id, deps in self.dependency_graph.items()
            }
        }
    
    def _format_response(self, captain_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format the captain's response into a standardized structure."""
        formatted_response = {
            "status": captain_result.get("status", "completed"),
            "timestamp": datetime.utcnow().isoformat(),
            "responses": captain_result.get("agent_responses", []),
            "summary": self._generate_summary(captain_result),
            "next_steps": self._extract_next_steps(captain_result),
            "metrics": self._extract_metrics(captain_result)
        }
        
        return formatted_response
    
    def _generate_summary(self, captain_result: Dict[str, Any]) -> str:
        """Generate a summary from the captain's result."""
        if not captain_result:
            return "No results to summarize"
        
        summary_points = []
        
        # Extract status information
        if "status" in captain_result:
            summary_points.append(f"Task status: {captain_result['status']}")
        
        # Extract agent contributions
        if "agent_responses" in captain_result:
            for response in captain_result["agent_responses"]:
                if isinstance(response, dict):
                    if "agent" in response:
                        summary_points.append(f"Input from {response['agent']}")
                    if "impact" in response:
                        summary_points.append(f"Impact: {response['impact']}")
        
        # Include captain's analysis if available
        if "analysis" in captain_result:
            summary_points.append(f"Captain's analysis: {captain_result['analysis']}")
        
        return " | ".join(summary_points) if summary_points else "Task processed by swarm"
    
    def _extract_next_steps(self, captain_result: Dict[str, Any]) -> List[str]:
        """Extract next steps from the captain's result."""
        next_steps = []
        
        # Extract recommendations from captain
        if "recommendations" in captain_result:
            next_steps.extend(captain_result["recommendations"])
        
        # Extract follow-up actions from agent responses
        if "agent_responses" in captain_result:
            for response in captain_result["agent_responses"]:
                if isinstance(response, dict):
                    if "follow_up" in response:
                        next_steps.extend(response["follow_up"])
                    if "opportunities" in response:
                        next_steps.extend([f"Explore {opp}" for opp in response["opportunities"]])
        
        # Add default steps if none were found
        if not next_steps:
            next_steps = [
                "Review results and metrics",
                "Implement suggested optimizations",
                "Monitor performance changes",
                "Schedule follow-up assessment",
                "Strengthen local partnerships"
            ]
        
        return next_steps
    
    def _extract_metrics(self, captain_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract performance metrics from the result."""
        metrics = {
            "response_time": captain_result.get("response_time", 0),
            "agent_participation": len(captain_result.get("agent_responses", [])),
            "task_complexity": captain_result.get("complexity_score", 0),
            "channel_usage": {
                name: channel.get_usage_metrics()
                for name, channel in self.channels.items()
            }
        }
        
        return metrics 