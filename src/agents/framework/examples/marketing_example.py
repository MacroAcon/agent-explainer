import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
sys.path.insert(0, project_root)

from src.agents.local_marketing_agent import LocalMarketingAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_marketing_demo():
    """Run a demonstration of the marketing capabilities"""
    
    # Create a marketing agent
    marketing_agent = LocalMarketingAgent(name="LocalMarketingDemo")
    
    print("=== Local Marketing Demo ===\n")
    
    # Demo 1: Create a social media campaign
    print("Demo 1: Creating a social media campaign\n")
    
    social_result = await marketing_agent.manage_social_media(
        social_data={
            "facebook_posts": [
                {
                    "content": "Join us for our Summer Sale! 20% off all items this weekend!",
                    "scheduled_time": (datetime.now() + timedelta(days=1)).isoformat(),
                    "media": ["summer_sale.jpg"]
                }
            ],
            "instagram_posts": [
                {
                    "content": "Check out our new summer collection! 🌞 #CalhounGA #ShopLocal",
                    "scheduled_time": (datetime.now() + timedelta(days=2)).isoformat(),
                    "media": ["summer_collection.jpg"]
                }
            ],
            "nextdoor_posts": [
                {
                    "content": "Local business spotlight: Come visit us at 123 Main St!",
                    "scheduled_time": (datetime.now() + timedelta(days=3)).isoformat()
                }
            ]
        },
        context={}
    )
    
    print("Social Media Campaign Created:")
    print(f"Campaign ID: {social_result['social_id']}")
    print("Platforms configured: Facebook, Instagram, Nextdoor")
    print("\n" + "-" * 80 + "\n")
    
    # Demo 2: Create a local promotion
    print("Demo 2: Creating a local promotion\n")
    
    promotion_result = await marketing_agent.create_promotion(
        promotion_data={
            "name": "Summer Weekend Sale",
            "type": "discount",
            "details": {
                "discount_percentage": 20,
                "valid_items": "all",
                "exclusions": ["clearance"]
            },
            "target_audience": ["local_residents", "shopping_enthusiasts"],
            "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=3)).isoformat()
        },
        context={}
    )
    
    print("Local Promotion Created:")
    print(f"Promotion ID: {promotion_result['promotion_id']}")
    print(f"Name: {promotion_result['name']}")
    print(f"Duration: {promotion_result['duration']['start']} to {promotion_result['duration']['end']}")
    print("\n" + "-" * 80 + "\n")
    
    # Demo 3: Create a marketing campaign
    print("Demo 3: Creating a comprehensive marketing campaign\n")
    
    campaign_result = await marketing_agent.create_campaign(
        campaign_data={
            "name": "Summer Collection Launch",
            "type": "product_launch",
            "target_audience": {
                "demographics": ["18-45"],
                "interests": ["fashion", "shopping"],
                "location": "Calhoun, GA"
            },
            "channels": ["social_media", "email", "local_media"],
            "budget": 5000.00,
            "start_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat()
        },
        context={}
    )
    
    print("Marketing Campaign Created:")
    print(f"Campaign ID: {campaign_result['campaign_id']}")
    print(f"Name: {campaign_result['name']}")
    print(f"Budget: ${campaign_result['budget']}")
    print(f"Duration: {campaign_result['timeline']['start']} to {campaign_result['timeline']['end']}")
    print("\n" + "-" * 80 + "\n")
    
    # Demo 4: Plan a community event
    print("Demo 4: Planning a community event\n")
    
    event_result = await marketing_agent.plan_events(
        event_data={
            "name": "Summer Fashion Show",
            "type": "community_event",
            "date": (datetime.now() + timedelta(days=15)).isoformat(),
            "location": "Downtown Calhoun Square",
            "budget": 2000.00,
            "partners": ["local_boutiques", "fashion_designers"],
            "activities": [
                "fashion_show",
                "local_vendor_booths",
                "refreshments",
                "live_music"
            ]
        },
        context={}
    )
    
    print("Community Event Planned:")
    print(f"Event ID: {event_result['event_id']}")
    print(f"Name: {event_result['name']}")
    print(f"Date: {event_result['date']}")
    print(f"Location: {event_result['location']}")
    print(f"Budget: ${event_result['budget']}")
    print("\n" + "-" * 80 + "\n")
    
    print("=== Marketing Demo Complete ===\n")
    print("This demo showed how the marketing agent can:")
    print("1. Create and manage social media campaigns")
    print("2. Design and launch local promotions")
    print("3. Develop comprehensive marketing campaigns")
    print("4. Plan and coordinate community events")
    print("\nThe agent provides a complete solution for local business marketing needs")

if __name__ == "__main__":
    asyncio.run(run_marketing_demo()) 