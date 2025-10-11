"""
Tools package for the IaC Agent
"""

from .validation import (
    validate_required_params,
    validate_ec2_creation_params,
    validate_security_group_creation_params,
    validate_rule_addition_params
)

from .key_pair_tools import (
    create_key_pair,
    list_key_pairs,
    delete_key_pair,
    get_key_pair_details
)

from .ec2_tools import (
    get_available_regions,
    get_instance_type_info,
    get_latest_amazon_linux_ami,
    create_ec2_instance,
    list_ec2_instances,
    terminate_ec2_instance,
    stop_ec2_instance,
    start_ec2_instance
)

from .security_group_tools import (
    list_security_groups,
    create_security_group,
    add_inbound_rule,
    add_outbound_rule,
    remove_inbound_rule,
    remove_outbound_rule,
    get_security_group_details,
    delete_security_group,
    create_web_server_security_group
)

from .data_collection import (
    get_data_collection_status
)

__all__ = [
    # Validation
    'validate_required_params',
    'validate_ec2_creation_params',
    'validate_security_group_creation_params',
    'validate_rule_addition_params',
    
    # Key Pair Tools
    'create_key_pair',
    'list_key_pairs',
    'delete_key_pair',
    'get_key_pair_details',
    
    # EC2 Tools
    'get_available_regions',
    'get_instance_type_info',
    'get_latest_amazon_linux_ami',
    'create_ec2_instance',
    'list_ec2_instances',
    'terminate_ec2_instance',
    'stop_ec2_instance',
    'start_ec2_instance',
    
    # Security Group Tools
    'list_security_groups',
    'create_security_group',
    'add_inbound_rule',
    'add_outbound_rule',
    'remove_inbound_rule',
    'remove_outbound_rule',
    'get_security_group_details',
    'delete_security_group',
    'create_web_server_security_group',
    
    # Data Collection
    'get_data_collection_status'
]
