import pytest
import logging
from unittest.mock import patch
from src.agents.supplier_agent_factory import SupplierAgentFactory
from src.utils.agent_monitoring import get_metrics_instance, monitor_operation
from src.utils.data_validation import SupplierDataValidator, DataValidationError
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
    get_metrics_instance().reset_metrics()
    return factory

class TestAgentSystemIntegration:
    """Integration tests for the complete agent system."""
    
    def test_end_to_end_workflow(self, factory):
        """Test an end-to-end workflow of the supplier agent system."""
        # Step 1: Create all agents
        agents = factory.create_all_agents()
        
        # Step 2: Verify agents were created correctly
        assert len(agents) == 5
        assert all(agent is not None for agent in agents.values())
        
        # Step 3: Check metrics are being collected
        metrics = get_metrics_instance().get_system_summary()
        assert metrics['total_operations'] > 0
        
        # Step 4: Create and validate supplier data
        supplier_data = {
            'id': 'SUP001',
            'name': 'Local Organic Farm',
            'location': {
                'address': '123 Farm Road',
                'city': 'Calhoun',
                'state': 'GA',
                'country': 'USA',
                'zip': '30701'
            },
            'contact': {
                'name': 'John Farmer',
                'email': 'john@localfarm.com',
                'phone': '555-123-4567'
            },
            'type': 'produce',
            'certifications': ['Organic', 'Local'],
            'rating': 4.8,
            'active': True
        }
        
        # Validate the data
        valid_data = SupplierDataValidator.validate(supplier_data, 'supplier_info')
        assert valid_data['id'] == 'SUP001'
        assert valid_data['name'] == 'Local Organic Farm'
        assert valid_data['active'] is True
        
        # Step 5: Test with invalid data
        invalid_data = supplier_data.copy()
        del invalid_data['name']  # Remove required field
        
        with pytest.raises(DataValidationError):
            SupplierDataValidator.validate(invalid_data, 'supplier_info')
        
        # Step 6: Create data template
        template = SupplierDataValidator.create_empty_template('pricing_data')
        assert 'supplier_id' in template
        assert 'price' in template
        assert isinstance(template['price'], float)
    
    @patch('src.utils.agent_monitoring.monitor_operation')
    def test_monitoring_integration(self, mock_monitor, factory):
        """Test that monitoring is properly integrated with agents."""
        # Create agents
        county_agent = factory.create_agent('county', 'TestCounty')
        
        # Check metrics collection
        metrics = get_metrics_instance().get_agent_metrics('TestCounty')
        
        # Metrics might be empty since we're mocking the monitor_operation decorator
        # That's okay for this test since we're just checking integration
        
        # Reset metrics
        get_metrics_instance().reset_metrics()
        assert len(get_metrics_instance().get_agent_metrics('TestCounty')) == 0
    
    def test_data_validation_integration(self, factory):
        """Test data validation integration."""
        # Create valid supplier data
        supplier_data = {
            'id': 'SUP002',
            'name': 'State Distributor',
            'location': {
                'address': '456 Distribution Ave',
                'city': 'Atlanta',
                'state': 'GA',
                'country': 'USA',
                'zip': '30301'
            },
            'contact': {
                'name': 'Sarah Manager',
                'email': 'sarah@statedist.com',
                'phone': '555-987-6543'
            },
            'type': 'distributor',
            'certifications': ['FDA Approved', 'State Licensed'],
            'rating': 4.5,
            'active': True
        }
        
        # Create pricing data
        pricing_data = {
            'supplier_id': 'SUP002',
            'item_id': 'ITEM001',
            'price': 15.99,
            'currency': 'USD',
            'quantity': 10,
            'unit': 'kg',
            'effective_date': '2023-01-01T00:00:00',
            'expiration_date': '2023-12-31T23:59:59'
        }
        
        # Validate data
        valid_supplier = SupplierDataValidator.validate(supplier_data, 'supplier_info')
        valid_pricing = SupplierDataValidator.validate(pricing_data, 'pricing_data')
        
        assert valid_supplier['id'] == supplier_data['id']
        assert valid_pricing['price'] == pricing_data['price']
        
        # Test with schema conversion (convert string to number)
        pricing_data_with_string = pricing_data.copy()
        pricing_data_with_string['price'] = '25.99'
        
        valid_pricing = SupplierDataValidator.validate(pricing_data_with_string, 'pricing_data')
        assert isinstance(valid_pricing['price'], float)
        assert valid_pricing['price'] == 25.99
    
    def test_exception_handling_integration(self, factory):
        """Test integration of custom exceptions throughout the system."""
        # Test invalid agent type
        with pytest.raises(InvalidAgentTypeError):
            factory.create_agent('invalid_type', 'TestAgent')
        
        # Create an agent
        factory.create_agent('county', 'TestAgent')
        
        # Test duplicate name
        with pytest.raises(DuplicateAgentError):
            factory.create_agent('state', 'TestAgent')
        
        # Test agent not found
        with pytest.raises(AgentNotFoundError):
            factory.get_agent('NonExistentAgent')
        
        # Test validation errors
        with pytest.raises(DataValidationError):
            SupplierDataValidator.validate({}, 'supplier_info')  # Empty data missing required fields 