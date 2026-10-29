"""
Data collection tools for the IaC Agent
"""

from strands import tool


@tool
def get_data_collection_status(operation: str, collected_data: dict = None) -> str:
    """
    Check what information has been collected for an operation

    Args:
        operation: The operation being performed (e.g., 'create_ec2_instance', 'create_security_group')
        collected_data: Dictionary of data collected so far (optional)

    Returns:
        Status of data collection with missing fields
    """
    if collected_data is None:
        collected_data = {}
    required_fields = {
        'create_ec2_instance': ['region', 'instance_type', 'instance_name'],
        'create_security_group': ['region', 'group_name', 'description'],
        'add_inbound_rule': ['region', 'security_group_id', 'protocol', 'port', 'source_ip'],
        'add_outbound_rule': ['region', 'security_group_id', 'protocol', 'port', 'destination_ip']
    }

    if operation not in required_fields:
        return f"Unknown operation: {operation}"

    missing_fields = []
    for field in required_fields[operation]:
        if field not in collected_data or collected_data[field] is None or collected_data[field] == "":
            missing_fields.append(field)

    if not missing_fields:
        return f"✅ All required data collected for {operation}. Ready to proceed!"
    else:
        return f"❌ Missing required fields for {operation}: {', '.join(missing_fields)}. Please collect these before proceeding."
