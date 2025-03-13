from typing import Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
from .hipaa_compliant_agent import HIPAACompliantAgent

class RestaurantOperationsAgent(HIPAACompliantAgent):
    """Agent for managing restaurant-specific operations in Calhoun, GA."""
    
    def __init__(self, name: str = "RestaurantOps"):
        system_message = """You are a restaurant operations specialist for businesses in Calhoun, GA, responsible for:
        1. Managing menu items and specials
        2. Kitchen operations and food preparation
        3. Quality control and food safety
        4. Table and seating management
        5. Bar operations and alcohol compliance
        6. Food cost analysis and pricing
        7. Kitchen staff coordination
        8. Equipment maintenance tracking
        9. Food waste management
        10. Special dietary accommodations
        11. Catering operations
        12. Local ingredient sourcing
        """
        
        tools = [
            {
                "name": "manage_menu",
                "description": "Manage menu items and specials",
                "func": self.manage_menu
            },
            {
                "name": "manage_kitchen",
                "description": "Manage kitchen operations",
                "func": self.manage_kitchen
            },
            {
                "name": "monitor_quality",
                "description": "Monitor food quality and safety",
                "func": self.monitor_quality
            },
            {
                "name": "manage_seating",
                "description": "Manage tables and seating",
                "func": self.manage_seating
            },
            {
                "name": "manage_bar",
                "description": "Manage bar operations",
                "func": self.manage_bar
            },
            {
                "name": "analyze_costs",
                "description": "Analyze food costs and pricing",
                "func": self.analyze_costs
            },
            {
                "name": "coordinate_staff",
                "description": "Coordinate kitchen staff",
                "func": self.coordinate_staff
            },
            {
                "name": "track_equipment",
                "description": "Track equipment maintenance",
                "func": self.track_equipment
            },
            {
                "name": "manage_waste",
                "description": "Manage food waste",
                "func": self.manage_waste
            },
            {
                "name": "handle_catering",
                "description": "Manage catering operations",
                "func": self.handle_catering
            }
        ]
        
        super().__init__(name=name, system_message=system_message, tools=tools)
    
    async def generate_response(self, message: Dict[str, Any]) -> str:
        """Generate a response using restaurant operations tools."""
        try:
            task = message["content"]
            context = message["context"]
            
            # Determine which tool to use based on task content
            if "menu" in task.lower():
                result = await self.manage_menu({"task": task, **context}, context)
                return self._format_tool_result("menu", result)
                
            elif "kitchen" in task.lower():
                result = await self.manage_kitchen({"task": task, **context}, context)
                return self._format_tool_result("kitchen", result)
                
            elif "quality" in task.lower() or "safety" in task.lower():
                result = await self.monitor_quality({"task": task, **context}, context)
                return self._format_tool_result("quality", result)
                
            elif "table" in task.lower() or "seating" in task.lower():
                result = await self.manage_seating({"task": task, **context}, context)
                return self._format_tool_result("seating", result)
                
            elif "bar" in task.lower() or "alcohol" in task.lower():
                result = await self.manage_bar({"task": task, **context}, context)
                return self._format_tool_result("bar", result)
                
            elif "cost" in task.lower() or "price" in task.lower():
                result = await self.analyze_costs({"task": task, **context}, context)
                return self._format_tool_result("costs", result)
                
            elif "staff" in task.lower() or "employee" in task.lower():
                result = await self.coordinate_staff({"task": task, **context}, context)
                return self._format_tool_result("staff", result)
                
            elif "equipment" in task.lower() or "maintenance" in task.lower():
                result = await self.track_equipment({"task": task, **context}, context)
                return self._format_tool_result("equipment", result)
                
            elif "waste" in task.lower():
                result = await self.manage_waste({"task": task, **context}, context)
                return self._format_tool_result("waste", result)
                
            elif "catering" in task.lower():
                result = await self.handle_catering({"task": task, **context}, context)
                return self._format_tool_result("catering", result)
                
            else:
                # Default to kitchen operations if no specific tool matches
                result = await self.manage_kitchen({"task": task, **context}, context)
                return self._format_tool_result("kitchen", result)
                
        except Exception as e:
            return f"Error in restaurant operations: {str(e)}"
    
    def _format_tool_result(self, tool_type: str, result: Dict[str, Any]) -> str:
        """Format tool results into a readable response."""
        if not result:
            return f"No {tool_type} information available"
            
        response_parts = []
        
        # Add ID and timestamp if available
        if f"{tool_type}_id" in result:
            response_parts.append(f"Operation ID: {result[f'{tool_type}_id']}")
        
        # Add main content based on tool type
        if tool_type == "menu":
            if "items" in result:
                response_parts.append("Menu Items:")
                for category, items in result["items"].items():
                    if items:
                        response_parts.append(f"- {category.title()}: {len(items)} items")
                        
        elif tool_type == "kitchen":
            if "prep_lists" in result:
                response_parts.append("Kitchen Operations:")
                for time, tasks in result["prep_lists"].items():
                    if tasks:
                        response_parts.append(f"- {time.title()} Prep: {len(tasks)} tasks")
                        
        elif tool_type == "quality":
            if "quality_metrics" in result:
                response_parts.append("Quality Metrics:")
                for metric, data in result["quality_metrics"].items():
                    response_parts.append(f"- {metric.title()}: {len(data) if isinstance(data, list) else 'Updated'}")
                    
        elif tool_type == "seating":
            if "floor_plan" in result:
                response_parts.append("Seating Status:")
                if "current_status" in result:
                    for status, tables in result["current_status"].items():
                        response_parts.append(f"- {status.title()}: {len(tables)} tables")
                        
        elif tool_type == "bar":
            if "inventory" in result:
                response_parts.append("Bar Operations:")
                for category, items in result["inventory"].items():
                    response_parts.append(f"- {category.title()}: {len(items) if items else 0} items")
                    
        elif tool_type == "costs":
            if "analysis" in result:
                response_parts.append("Cost Analysis:")
                for category, data in result["analysis"].items():
                    response_parts.append(f"- {category.replace('_', ' ').title()}")
                    
        elif tool_type == "staff":
            if "schedules" in result:
                response_parts.append("Staff Coordination:")
                for shift, staff in result["schedules"].items():
                    response_parts.append(f"- {shift.title()}: {len(staff) if staff else 0} staff")
                    
        elif tool_type == "equipment":
            if "maintenance" in result:
                response_parts.append("Equipment Status:")
                for status, items in result["maintenance"].items():
                    response_parts.append(f"- {status.replace('_', ' ').title()}: {len(items)} items")
                    
        elif tool_type == "waste":
            if "tracking" in result:
                response_parts.append("Waste Management:")
                for category, data in result["tracking"].items():
                    response_parts.append(f"- {category.replace('_', ' ').title()}")
                    
        elif tool_type == "catering":
            if "events" in result:
                response_parts.append("Catering Operations:")
                for status, events in result["events"].items():
                    response_parts.append(f"- {status.title()}: {len(events)} events")
        
        return "\n".join(response_parts)
    
    async def manage_menu(
        self,
        menu_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manage menu items, specials, and seasonal changes."""
        menu_result = {
            "menu_id": f"MNU{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            "categories": menu_data.get("categories", []),
            "items": {
                "regular": menu_data.get("regular_items", []),
                "specials": menu_data.get("daily_specials", []),
                "seasonal": menu_data.get("seasonal_items", [])
            },
            "pricing": {
                "current": menu_data.get("current_prices", {}),
                "suggested_updates": []
            },
            "dietary_options": {
                "vegetarian": [],
                "vegan": [],
                "gluten_free": [],
                "allergen_info": {}
            },
            "local_ingredients": {
                "current": [],
                "seasonal_availability": {},
                "suppliers": []
            },
            "popularity_metrics": {
                "top_sellers": [],
                "low_performers": [],
                "profit_margins": {}
            }
        }
        
        return menu_result
    
    async def manage_kitchen(
        self,
        kitchen_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manage kitchen operations and food preparation."""
        kitchen_result = {
            "kitchen_id": f"KIT{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            "prep_lists": {
                "morning": kitchen_data.get("morning_prep", []),
                "afternoon": kitchen_data.get("afternoon_prep", []),
                "evening": kitchen_data.get("evening_prep", [])
            },
            "station_assignments": kitchen_data.get("stations", {}),
            "recipe_specs": {
                "standard": kitchen_data.get("standard_recipes", {}),
                "specials": kitchen_data.get("special_recipes", {}),
                "prep": kitchen_data.get("prep_recipes", {})
            },
            "inventory_levels": {
                "critical": [],
                "low": [],
                "adequate": []
            },
            "equipment_status": {
                "operational": [],
                "maintenance_needed": [],
                "offline": []
            },
            "quality_checks": {
                "temperature_logs": [],
                "freshness_checks": [],
                "presentation_standards": []
            }
        }
        
        return kitchen_result
    
    async def monitor_quality(
        self,
        quality_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Monitor food quality and safety standards."""
        quality_result = {
            "quality_id": f"QUA{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            "temperature_logs": {
                "refrigeration": quality_data.get("fridge_temps", []),
                "cooking": quality_data.get("cooking_temps", []),
                "holding": quality_data.get("holding_temps", [])
            },
            "freshness_checks": {
                "produce": [],
                "proteins": [],
                "dairy": []
            },
            "sanitation": {
                "cleaning_schedule": quality_data.get("cleaning_schedule", {}),
                "inspection_points": [],
                "critical_issues": []
            },
            "allergen_control": {
                "cross_contamination": [],
                "special_handling": [],
                "staff_training": []
            },
            "quality_metrics": {
                "presentation": [],
                "taste": [],
                "consistency": []
            }
        }
        
        return quality_result
    
    async def manage_seating(
        self,
        seating_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manage table assignments and seating optimization."""
        seating_result = {
            "seating_id": f"SEA{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            "floor_plan": {
                "tables": seating_data.get("tables", {}),
                "sections": seating_data.get("sections", {}),
                "capacity": seating_data.get("capacity", {})
            },
            "current_status": {
                "occupied": [],
                "reserved": [],
                "available": []
            },
            "wait_list": {
                "current": [],
                "estimated_times": {}
            },
            "server_sections": {
                "assignments": {},
                "rotation": [],
                "load_balancing": {}
            },
            "special_arrangements": {
                "large_parties": [],
                "accessibility": [],
                "preferences": []
            }
        }
        
        return seating_result
    
    async def manage_bar(
        self,
        bar_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manage bar operations and alcohol service."""
        bar_result = {
            "bar_id": f"BAR{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            "inventory": {
                "spirits": bar_data.get("spirits", {}),
                "beer": bar_data.get("beer", {}),
                "wine": bar_data.get("wine", {}),
                "mixers": bar_data.get("mixers", {})
            },
            "drink_menu": {
                "cocktails": [],
                "specials": [],
                "happy_hour": []
            },
            "compliance": {
                "licenses": [],
                "certifications": [],
                "training_records": []
            },
            "sales_metrics": {
                "popular_items": [],
                "profit_margins": {},
                "waste_tracking": {}
            },
            "service_standards": {
                "recipes": {},
                "presentation": {},
                "pricing": {}
            }
        }
        
        return bar_result
    
    async def analyze_costs(
        self,
        cost_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze food costs and optimize pricing."""
        cost_result = {
            "analysis_id": f"CST{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            "ingredient_costs": {
                "raw_materials": cost_data.get("ingredients", {}),
                "processing": cost_data.get("processing", {}),
                "waste": cost_data.get("waste", {})
            },
            "menu_pricing": {
                "current": cost_data.get("current_prices", {}),
                "suggested": {},
                "competitor_comparison": {}
            },
            "profitability": {
                "by_item": {},
                "by_category": {},
                "trends": []
            },
            "cost_reduction": {
                "opportunities": [],
                "supplier_alternatives": [],
                "process_improvements": []
            },
            "seasonal_adjustments": {
                "projected": [],
                "historical": [],
                "market_factors": []
            }
        }
        
        return cost_result
    
    async def coordinate_staff(
        self,
        staff_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Coordinate kitchen staff and assignments."""
        staff_result = {
            "coordination_id": f"STF{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            "stations": {
                "line": staff_data.get("line_assignments", {}),
                "prep": staff_data.get("prep_assignments", {}),
                "specialty": staff_data.get("specialty_assignments", {})
            },
            "schedules": {
                "current": staff_data.get("current_schedule", {}),
                "upcoming": staff_data.get("upcoming_schedule", {}),
                "time_off": staff_data.get("time_off_requests", [])
            },
            "certifications": {
                "food_safety": [],
                "specialization": [],
                "required_training": []
            },
            "performance": {
                "metrics": {},
                "reviews": [],
                "training_needs": []
            }
        }
        
        return staff_result
    
    async def track_equipment(
        self,
        equipment_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track kitchen equipment maintenance and status."""
        equipment_result = {
            "tracking_id": f"EQP{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            "inventory": {
                "major_equipment": equipment_data.get("major_equipment", {}),
                "small_wares": equipment_data.get("small_wares", {}),
                "specialty_items": equipment_data.get("specialty_items", {})
            },
            "maintenance": {
                "scheduled": [],
                "completed": [],
                "needed": []
            },
            "repairs": {
                "active": [],
                "history": [],
                "costs": {}
            },
            "replacement_planning": {
                "upcoming": [],
                "budgeted": [],
                "emergency": []
            }
        }
        
        return equipment_result
    
    async def manage_waste(
        self,
        waste_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manage food waste and implement reduction strategies."""
        waste_result = {
            "waste_id": f"WST{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            "tracking": {
                "prep_waste": waste_data.get("prep_waste", {}),
                "plate_waste": waste_data.get("plate_waste", {}),
                "spoilage": waste_data.get("spoilage", {})
            },
            "reduction_strategies": {
                "portion_control": [],
                "inventory_management": [],
                "prep_optimization": []
            },
            "composting": {
                "program": {},
                "metrics": {},
                "partners": []
            },
            "donation_program": {
                "partners": [],
                "schedule": {},
                "metrics": {}
            },
            "cost_impact": {
                "weekly": 0.0,
                "monthly": 0.0,
                "trends": []
            }
        }
        
        return waste_result
    
    async def handle_catering(
        self,
        catering_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manage catering operations and events."""
        catering_result = {
            "catering_id": f"CAT{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            "events": {
                "upcoming": catering_data.get("upcoming_events", []),
                "completed": catering_data.get("completed_events", []),
                "inquiries": catering_data.get("inquiries", [])
            },
            "menus": {
                "packages": [],
                "custom": [],
                "pricing": {}
            },
            "logistics": {
                "staffing": {},
                "equipment": {},
                "transportation": {}
            },
            "contracts": {
                "templates": [],
                "active": [],
                "archived": []
            },
            "financials": {
                "deposits": {},
                "invoices": {},
                "profitability": {}
            }
        }
        
        return catering_result
    
    def _calculate_portion_cost(self, ingredients: Dict[str, Any]) -> Decimal:
        """Calculate the cost of a menu item's ingredients."""
        total_cost = Decimal('0.00')
        for ingredient, amount in ingredients.items():
            unit_cost = Decimal(str(amount.get("unit_cost", 0)))
            quantity = Decimal(str(amount.get("quantity", 0)))
            total_cost += unit_cost * quantity
        return total_cost
    
    def _calculate_menu_price(self, cost: Decimal, target_margin: Decimal) -> Decimal:
        """Calculate menu price based on cost and target margin."""
        return cost / (1 - target_margin)
    
    def _estimate_prep_time(self, recipe_data: Dict[str, Any]) -> int:
        """Estimate preparation time for a menu item in minutes."""
        base_time = recipe_data.get("base_time", 0)
        complexity_factor = recipe_data.get("complexity", 1.0)
        return int(base_time * complexity_factor) 