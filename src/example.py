import asyncio
from datetime import datetime, timedelta
from agents.swarm_coordinator import BusinessSwarmCoordinator

async def main():
    """Example of business automation for a restaurant in Calhoun, GA."""
    
    # Initialize the swarm coordinator
    coordinator = BusinessSwarmCoordinator()
    
    # Example tasks for a local restaurant
    tasks = [
        {
            "task": "Create a new seasonal menu using local ingredients and update pricing",
            "context": {
                "business_type": "restaurant",
                "business_name": "Downtown Calhoun Grill",
                "user_id": "CHEF_123",
                "access_level": "admin",
                "season": "summer",
                "local_suppliers": [
                    "Calhoun Farmers Market",
                    "Gordon County Farms",
                    "North Georgia Produce"
                ]
            }
        },
        {
            "task": "Coordinate bulk purchasing program with other local restaurants for seasonal produce",
            "context": {
                "business_type": "restaurant",
                "business_name": "Downtown Calhoun Grill",
                "user_id": "MANAGER_456",
                "access_level": "admin",
                "participating_businesses": [
                    "Calhoun Street Cafe",
                    "Gordon's Bistro",
                    "The Local Kitchen"
                ],
                "target_ingredients": [
                    "tomatoes",
                    "corn",
                    "peaches",
                    "berries"
                ],
                "program_duration": "summer_season"
            }
        },
        {
            "task": "Plan farm-to-table education series with local schools",
            "context": {
                "business_type": "restaurant",
                "business_name": "Downtown Calhoun Grill",
                "user_id": "COMMUNITY_789",
                "access_level": "write",
                "target_audience": "middle_school",
                "participating_schools": [
                    "Calhoun Middle School",
                    "Red Bud Middle School"
                ],
                "program_components": [
                    "Farm visits",
                    "Cooking demonstrations",
                    "Nutrition education",
                    "Sustainable farming practices"
                ]
            }
        },
        {
            "task": "Monitor and analyze local market prices for seasonal ingredients",
            "context": {
                "business_type": "restaurant",
                "business_name": "Downtown Calhoun Grill",
                "user_id": "ANALYST_101",
                "access_level": "read",
                "market_areas": [
                    "Calhoun",
                    "Gordon County",
                    "North Georgia"
                ],
                "ingredient_categories": [
                    "produce",
                    "dairy",
                    "proteins",
                    "specialty_items"
                ],
                "analysis_period": "quarterly"
            }
        },
        {
            "task": "Develop sustainability initiative with local farms",
            "context": {
                "business_type": "restaurant",
                "business_name": "Downtown Calhoun Grill",
                "user_id": "SUSTAINABILITY_202",
                "access_level": "admin",
                "initiative_focus": [
                    "Waste reduction",
                    "Composting program",
                    "Packaging alternatives",
                    "Water conservation"
                ],
                "partner_farms": [
                    "Green Valley Organics",
                    "Heritage Family Farm",
                    "Mountain View Gardens"
                ],
                "program_duration": "annual"
            }
        }
    ]
    
    # Process each task and print results
    for task_info in tasks:
        print(f"\nProcessing task: {task_info['task']}")
        print("Context:", task_info['context'])
        
        # Process task using AG2 swarm
        result = await coordinator.process_task(
            task=task_info['task'],
            context=task_info['context']
        )
        
        # Print task results
        print("\nTask Result:")
        print(f"Status: {result['status']}")
        print(f"Timestamp: {result['timestamp']}")
        
        # Print agent responses
        print("\nAgent Responses:")
        for response in result['responses']:
            if isinstance(response, dict):
                print(f"\nAgent: {response.get('agent', 'Unknown')}")
                print(f"Role: {response.get('role', 'Unknown')}")
                if 'response' in response:
                    print("Response:")
                    print(response['response'])
        
        # Print captain's analysis
        if result.get('summary'):
            print("\nCaptain's Analysis:")
            print(result['summary'])
        
        # Print next steps
        if result.get('next_steps'):
            print("\nRecommended Next Steps:")
            for step in result['next_steps']:
                print(f"- {step}")
        
        # Print task completion
        print("\n" + "="*50)
        
        # Optional: Get task status from captain
        status = await coordinator.get_task_status()
        if status:
            print("\nTask Status from Captain:")
            print(status)
            print("\n" + "="*50)

if __name__ == "__main__":
    asyncio.run(main()) 