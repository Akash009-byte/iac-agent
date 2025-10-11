#!/usr/bin/env python3
"""
Test script to verify that the agent collects all required data before calling tools
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from iac.interactive_strands_agent import (
    validate_ec2_creation_params,
    validate_security_group_creation_params,
    validate_rule_addition_params,
    get_data_collection_status
)


def test_validation_functions():
    """Test the validation functions"""
    
    print("🧪 Testing Data Collection Validation Functions")
    print("=" * 60)
    
    # Test EC2 creation validation
    print("\n=== Testing EC2 Creation Validation ===")
    
    # Valid parameters
    is_valid, error_msg = validate_ec2_creation_params("us-east-1", "t2.micro", "test-instance")
    print(f"✅ Valid params: {is_valid}, Error: {error_msg}")
    
    # Missing region
    is_valid, error_msg = validate_ec2_creation_params("", "t2.micro", "test-instance")
    print(f"❌ Missing region: {is_valid}, Error: {error_msg}")
    
    # Missing instance type
    is_valid, error_msg = validate_ec2_creation_params("us-east-1", "", "test-instance")
    print(f"❌ Missing instance type: {is_valid}, Error: {error_msg}")
    
    # Missing instance name
    is_valid, error_msg = validate_ec2_creation_params("us-east-1", "t2.micro", "")
    print(f"❌ Missing instance name: {is_valid}, Error: {error_msg}")
    
    # Test Security Group creation validation
    print("\n=== Testing Security Group Creation Validation ===")
    
    # Valid parameters
    is_valid, error_msg = validate_security_group_creation_params("us-east-1", "test-sg", "Test security group")
    print(f"✅ Valid params: {is_valid}, Error: {error_msg}")
    
    # Missing group name
    is_valid, error_msg = validate_security_group_creation_params("us-east-1", "", "Test security group")
    print(f"❌ Missing group name: {is_valid}, Error: {error_msg}")
    
    # Missing description
    is_valid, error_msg = validate_security_group_creation_params("us-east-1", "test-sg", "")
    print(f"❌ Missing description: {is_valid}, Error: {error_msg}")
    
    # Test Rule addition validation
    print("\n=== Testing Rule Addition Validation ===")
    
    # Valid parameters
    is_valid, error_msg = validate_rule_addition_params("us-east-1", "sg-12345678", "tcp", 80, "0.0.0.0/0")
    print(f"✅ Valid params: {is_valid}, Error: {error_msg}")
    
    # Missing security group ID
    is_valid, error_msg = validate_rule_addition_params("us-east-1", "", "tcp", 80, "0.0.0.0/0")
    print(f"❌ Missing security group ID: {is_valid}, Error: {error_msg}")
    
    # Missing protocol
    is_valid, error_msg = validate_rule_addition_params("us-east-1", "sg-12345678", "", 80, "0.0.0.0/0")
    print(f"❌ Missing protocol: {is_valid}, Error: {error_msg}")


def test_data_collection_status():
    """Test the data collection status function"""
    
    print("\n=== Testing Data Collection Status ===")
    
    # Test EC2 instance creation
    collected_data = {
        'region': 'us-east-1',
        'instance_type': 't2.micro',
        'instance_name': 'test-instance'
    }
    status = get_data_collection_status('create_ec2_instance', collected_data)
    print(f"✅ Complete EC2 data: {status}")
    
    # Test incomplete EC2 data
    incomplete_data = {
        'region': 'us-east-1',
        'instance_type': 't2.micro'
        # Missing instance_name
    }
    status = get_data_collection_status('create_ec2_instance', incomplete_data)
    print(f"❌ Incomplete EC2 data: {status}")
    
    # Test Security Group creation
    sg_data = {
        'region': 'us-east-1',
        'group_name': 'test-sg',
        'description': 'Test security group'
    }
    status = get_data_collection_status('create_security_group', sg_data)
    print(f"✅ Complete SG data: {status}")
    
    # Test incomplete Security Group data
    incomplete_sg_data = {
        'region': 'us-east-1',
        'group_name': 'test-sg'
        # Missing description
    }
    status = get_data_collection_status('create_security_group', incomplete_sg_data)
    print(f"❌ Incomplete SG data: {status}")
    
    # Test Rule addition
    rule_data = {
        'region': 'us-east-1',
        'security_group_id': 'sg-12345678',
        'protocol': 'tcp',
        'port': 80,
        'source_ip': '0.0.0.0/0'
    }
    status = get_data_collection_status('add_inbound_rule', rule_data)
    print(f"✅ Complete rule data: {status}")
    
    # Test incomplete Rule data
    incomplete_rule_data = {
        'region': 'us-east-1',
        'security_group_id': 'sg-12345678',
        'protocol': 'tcp'
        # Missing port and source_ip
    }
    status = get_data_collection_status('add_inbound_rule', incomplete_rule_data)
    print(f"❌ Incomplete rule data: {status}")


def simulate_agent_conversation():
    """Simulate how the agent should collect data"""
    
    print("\n=== Simulating Agent Conversation Flow ===")
    
    # Simulate EC2 instance creation conversation
    print("\n🤖 Agent: I'd like to help you create an EC2 instance. First, which AWS region would you like to use?")
    print("👤 User: us-east-1")
    
    collected_data = {'region': 'us-east-1'}
    status = get_data_collection_status('create_ec2_instance', collected_data)
    print(f"🔍 Status: {status}")
    
    print("\n🤖 Agent: Great! What instance type would you like? (e.g., t2.micro, t3.small)")
    print("👤 User: t2.micro")
    
    collected_data['instance_type'] = 't2.micro'
    status = get_data_collection_status('create_ec2_instance', collected_data)
    print(f"🔍 Status: {status}")
    
    print("\n🤖 Agent: What would you like to name this instance?")
    print("👤 User: my-test-instance")
    
    collected_data['instance_name'] = 'my-test-instance'
    status = get_data_collection_status('create_ec2_instance', collected_data)
    print(f"🔍 Status: {status}")
    
    print("\n🤖 Agent: Perfect! Now I have all the required information. Let me create your EC2 instance...")
    
    # Now validate the parameters
    is_valid, error_msg = validate_ec2_creation_params(
        collected_data['region'],
        collected_data['instance_type'],
        collected_data['instance_name']
    )
    
    if is_valid:
        print("✅ Validation passed! Ready to create EC2 instance.")
    else:
        print(f"❌ Validation failed: {error_msg}")


if __name__ == "__main__":
    test_validation_functions()
    test_data_collection_status()
    simulate_agent_conversation()
    
    print("\n" + "=" * 60)
    print("🎯 Key Takeaways:")
    print("1. Agent must collect ALL required data before calling tools")
    print("2. Validation functions prevent incomplete tool calls")
    print("3. Data collection status helps track progress")
    print("4. Step-by-step conversation ensures completeness")
    print("5. Always confirm data before proceeding with operations")
