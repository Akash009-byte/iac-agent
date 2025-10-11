"""
Validation functions for the IaC Agent tools
"""

from typing import Dict, List, Tuple


def validate_required_params(params: Dict, required_fields: List[str]) -> Tuple[bool, str]:
    """
    Validate that all required parameters are provided
    
    Args:
        params: Dictionary of parameters to validate
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    missing_fields = []
    for field in required_fields:
        if field not in params or params[field] is None or params[field] == "":
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required parameters: {', '.join(missing_fields)}"
    
    return True, ""


def validate_ec2_creation_params(region: str, instance_type: str, instance_name: str) -> Tuple[bool, str]:
    """Validate EC2 instance creation parameters"""
    required_fields = ['region', 'instance_type', 'instance_name']
    params = {
        'region': region,
        'instance_type': instance_type,
        'instance_name': instance_name
    }
    return validate_required_params(params, required_fields)


def validate_security_group_creation_params(region: str, group_name: str, description: str) -> Tuple[bool, str]:
    """Validate security group creation parameters"""
    required_fields = ['region', 'group_name', 'description']
    params = {
        'region': region,
        'group_name': group_name,
        'description': description
    }
    return validate_required_params(params, required_fields)


def validate_rule_addition_params(region: str, security_group_id: str, protocol: str, port: int, ip_range: str) -> Tuple[bool, str]:
    """Validate security group rule addition parameters"""
    required_fields = ['region', 'security_group_id', 'protocol', 'port', 'ip_range']
    params = {
        'region': region,
        'security_group_id': security_group_id,
        'protocol': protocol,
        'port': port,
        'ip_range': ip_range
    }
    return validate_required_params(params, required_fields)


def validate_key_pair_creation_params(region: str, key_name: str) -> Tuple[bool, str]:
    """Validate key pair creation parameters"""
    required_fields = ['region', 'key_name']
    params = {
        'region': region,
        'key_name': key_name
    }
    return validate_required_params(params, required_fields)
