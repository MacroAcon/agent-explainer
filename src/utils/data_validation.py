from typing import Dict, Any, List, Optional, Union
import logging
import json
from datetime import datetime
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataValidationError(Exception):
    """Exception raised for data validation errors."""
    pass

class SupplierDataValidator:
    """Utility class for validating supplier data formats."""
    
    # Schema definitions for different supplier data types
    SCHEMAS = {
        'supplier_info': {
            'id': {'type': 'string', 'required': True},
            'name': {'type': 'string', 'required': True},
            'location': {'type': 'dict', 'required': True},
            'contact': {'type': 'dict', 'required': True},
            'type': {'type': 'string', 'required': True},
            'certifications': {'type': 'list', 'required': False},
            'rating': {'type': 'number', 'required': False},
            'active': {'type': 'boolean', 'required': True}
        },
        'pricing_data': {
            'supplier_id': {'type': 'string', 'required': True},
            'item_id': {'type': 'string', 'required': True},
            'price': {'type': 'number', 'required': True},
            'currency': {'type': 'string', 'required': True},
            'quantity': {'type': 'number', 'required': True},
            'unit': {'type': 'string', 'required': True},
            'effective_date': {'type': 'date', 'required': True},
            'expiration_date': {'type': 'date', 'required': False}
        },
        'logistics_info': {
            'supplier_id': {'type': 'string', 'required': True},
            'shipping_methods': {'type': 'list', 'required': True},
            'delivery_time': {'type': 'dict', 'required': True},
            'shipping_costs': {'type': 'dict', 'required': False},
            'restrictions': {'type': 'list', 'required': False}
        },
        'compliance_data': {
            'supplier_id': {'type': 'string', 'required': True},
            'certifications': {'type': 'list', 'required': True},
            'audit_history': {'type': 'list', 'required': False},
            'compliance_score': {'type': 'number', 'required': False},
            'expiration_dates': {'type': 'dict', 'required': True}
        },
        'performance_metrics': {
            'supplier_id': {'type': 'string', 'required': True},
            'on_time_delivery': {'type': 'number', 'required': True},
            'quality_score': {'type': 'number', 'required': True},
            'response_time': {'type': 'number', 'required': False},
            'cost_efficiency': {'type': 'number', 'required': False},
            'period': {'type': 'dict', 'required': True}
        }
    }
    
    @staticmethod
    def validate(data: Dict[str, Any], schema_name: str) -> Dict[str, Any]:
        """
        Validate data against a schema.
        
        Args:
            data: Data to validate
            schema_name: Name of the schema to validate against
            
        Returns:
            The validated data (potentially with defaults applied)
            
        Raises:
            DataValidationError: If validation fails
        """
        if schema_name not in SupplierDataValidator.SCHEMAS:
            raise DataValidationError(f"Unknown schema: {schema_name}")
        
        schema = SupplierDataValidator.SCHEMAS[schema_name]
        
        # Check for required fields
        for field, field_spec in schema.items():
            if field_spec.get('required', False) and field not in data:
                raise DataValidationError(f"Required field '{field}' missing in {schema_name} data")
        
        # Validate field types
        validated_data = {}
        for field, value in data.items():
            # Skip fields not in schema
            if field not in schema:
                logger.warning(f"Field '{field}' not in {schema_name} schema - ignoring")
                continue
            
            field_spec = schema[field]
            validated_data[field] = SupplierDataValidator._validate_field(
                field, value, field_spec.get('type'), schema_name
            )
        
        return validated_data
    
    @staticmethod
    def _validate_field(field: str, value: Any, field_type: str, schema_name: str) -> Any:
        """
        Validate a field against its expected type.
        
        Args:
            field: Field name
            value: Field value
            field_type: Expected field type
            schema_name: Name of the schema being validated
            
        Returns:
            The validated value (potentially converted)
            
        Raises:
            DataValidationError: If validation fails
        """
        if value is None:
            return None
        
        if field_type == 'string':
            if not isinstance(value, str):
                if isinstance(value, (int, float, bool)):
                    return str(value)
                raise DataValidationError(
                    f"Field '{field}' in {schema_name} should be a string, got {type(value).__name__}"
                )
        
        elif field_type == 'number':
            if not isinstance(value, (int, float, Decimal)):
                try:
                    return float(value)
                except (ValueError, TypeError):
                    raise DataValidationError(
                        f"Field '{field}' in {schema_name} should be a number, got {type(value).__name__}"
                    )
        
        elif field_type == 'boolean':
            if not isinstance(value, bool):
                if value in ('true', 'True', '1', 1):
                    return True
                elif value in ('false', 'False', '0', 0):
                    return False
                raise DataValidationError(
                    f"Field '{field}' in {schema_name} should be a boolean, got {type(value).__name__}"
                )
        
        elif field_type == 'date':
            if isinstance(value, str):
                try:
                    # Try to parse the string as a date
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    raise DataValidationError(
                        f"Field '{field}' in {schema_name} should be a valid date string in ISO format"
                    )
            elif not isinstance(value, datetime):
                raise DataValidationError(
                    f"Field '{field}' in {schema_name} should be a date, got {type(value).__name__}"
                )
        
        elif field_type == 'list':
            if not isinstance(value, (list, tuple)):
                raise DataValidationError(
                    f"Field '{field}' in {schema_name} should be a list, got {type(value).__name__}"
                )
        
        elif field_type == 'dict':
            if not isinstance(value, dict):
                raise DataValidationError(
                    f"Field '{field}' in {schema_name} should be a dictionary, got {type(value).__name__}"
                )
        
        return value
    
    @staticmethod
    def validate_json(json_data: str, schema_name: str) -> Dict[str, Any]:
        """
        Validate JSON data against a schema.
        
        Args:
            json_data: JSON string to validate
            schema_name: Name of the schema to validate against
            
        Returns:
            The validated data as a dictionary
            
        Raises:
            DataValidationError: If validation fails
        """
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            raise DataValidationError(f"Invalid JSON data: {str(e)}")
        
        return SupplierDataValidator.validate(data, schema_name)
    
    @staticmethod
    def get_schema(schema_name: str) -> Dict[str, Any]:
        """
        Get a schema by name.
        
        Args:
            schema_name: Name of the schema
            
        Returns:
            Schema definition
            
        Raises:
            DataValidationError: If schema does not exist
        """
        if schema_name not in SupplierDataValidator.SCHEMAS:
            raise DataValidationError(f"Unknown schema: {schema_name}")
        
        return SupplierDataValidator.SCHEMAS[schema_name].copy()
    
    @staticmethod
    def create_empty_template(schema_name: str) -> Dict[str, Any]:
        """
        Create an empty data template for a schema.
        
        Args:
            schema_name: Name of the schema
            
        Returns:
            Empty template with default values
            
        Raises:
            DataValidationError: If schema does not exist
        """
        if schema_name not in SupplierDataValidator.SCHEMAS:
            raise DataValidationError(f"Unknown schema: {schema_name}")
        
        schema = SupplierDataValidator.SCHEMAS[schema_name]
        template = {}
        
        for field, field_spec in schema.items():
            if field_spec.get('type') == 'string':
                template[field] = ""
            elif field_spec.get('type') == 'number':
                template[field] = 0.0
            elif field_spec.get('type') == 'boolean':
                template[field] = False
            elif field_spec.get('type') == 'date':
                template[field] = datetime.now().isoformat()
            elif field_spec.get('type') == 'list':
                template[field] = []
            elif field_spec.get('type') == 'dict':
                template[field] = {}
        
        return template 