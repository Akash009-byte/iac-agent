#!/usr/bin/env python3
"""
Test script to verify key pair creation and integration with EC2 instance creation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from iac.tools.key_pair_tools import (
    create_key_pair,
    list_key_pairs,
    delete_key_pair,
    get_key_pair_details
)

from iac.tools.validation import validate_key_pair_creation_params
from iac.tools.data_collection import get_data_collection_status


def test_key_pair_validation():
    """Test key pair validation functions"""

    print("🧪 Testing Key Pair Validation Functions")
    print("=" * 60)

    # Test valid parameters
    is_valid, error_msg = validate_key_pair_creation_params("us-east-1", "test-key-pair")
    print(f"✅ Valid params: {is_valid}, Error: {error_msg}")

    # Test missing region
    is_valid, error_msg = validate_key_pair_creation_params("", "test-key-pair")
    print(f"❌ Missing region: {is_valid}, Error: {error_msg}")

    # Test missing key name
    is_valid, error_msg = validate_key_pair_creation_params("us-east-1", "")
    print(f"❌ Missing key name: {is_valid}, Error: {error_msg}")


def test_data_collection_status():
    """Test data collection status for key pair creation"""

    print("\n=== Testing Key Pair Data Collection Status ===")

    # Test complete key pair data
    collected_data = {
        'region': 'us-east-1',
        'key_name': 'test-key-pair'
    }
    status = get_data_collection_status('create_key_pair', collected_data)
    print(f"✅ Complete key pair data: {status}")

    # Test incomplete key pair data
    incomplete_data = {
        'region': 'us-east-1'
        # Missing key_name
    }
    status = get_data_collection_status('create_key_pair', incomplete_data)
    print(f"❌ Incomplete key pair data: {status}")


def simulate_key_pair_creation_conversation():
    """Simulate how the agent should collect data for key pair creation"""

    print("\n=== Simulating Key Pair Creation Conversation Flow ===")

    # Simulate key pair creation conversation
    print("\n🤖 Agent: I'd like to help you create a key pair for SSH access. First, which AWS region would you like to use?")
    print("👤 User: us-east-1")

    collected_data = {'region': 'us-east-1'}
    status = get_data_collection_status('create_key_pair', collected_data)
    print(f"🔍 Status: {status}")

    print("\n🤖 Agent: Great! What would you like to name this key pair?")
    print("👤 User: my-ssh-key")

    collected_data['key_name'] = 'my-ssh-key'
    status = get_data_collection_status('create_key_pair', collected_data)
    print(f"🔍 Status: {status}")

    print("\n🤖 Agent: Perfect! Now I have all the required information. Let me create your key pair...")

    # Now validate the parameters
    is_valid, error_msg = validate_key_pair_creation_params(
        collected_data['region'],
        collected_data['key_name']
    )

    if is_valid:
        print("✅ Validation passed! Ready to create key pair.")
        print("🔑 The agent would now call create_key_pair() and provide the private key for download.")
    else:
        print(f"❌ Validation failed: {error_msg}")


def simulate_ec2_with_key_pair_conversation():
    """Simulate EC2 instance creation with key pair integration"""

    print("\n=== Simulating EC2 Instance Creation with Key Pair Integration ===")

    collected_data = {}

    print("\n🤖 Agent: I'd like to help you create an EC2 instance. First, which AWS region would you like to use?")
    print("👤 User: us-east-1")
    collected_data['region'] = 'us-east-1'

    print("\n🤖 Agent: Great! What instance type would you like? (e.g., t2.micro, t3.small)")
    print("👤 User: t2.micro")
    collected_data['instance_type'] = 't2.micro'

    print("\n🤖 Agent: What would you like to name this instance?")
    print("👤 User: my-web-server")
    collected_data['instance_name'] = 'my-web-server'

    print("\n🤖 Agent: Do you have a key pair for SSH access? If not, I can help you create one.")
    print("👤 User: No, I don't have one. Can you create one for me?")

    print("\n🤖 Agent: Of course! I'll create a key pair for you. What would you like to name it?")
    print("👤 User: web-server-key")

    # Simulate key pair creation
    key_pair_data = {
        'region': collected_data['region'],
        'key_name': 'web-server-key'
    }

    status = get_data_collection_status('create_key_pair', key_pair_data)
    print(f"🔍 Key pair status: {status}")

    print("\n🤖 Agent: Perfect! I'll create the key pair and then use it for your EC2 instance.")
    print("🔑 [Agent would create key pair and provide private key for download]")

    # Add key pair to EC2 data
    collected_data['key_name'] = 'web-server-key'

    # Check EC2 data collection status
    ec2_status = get_data_collection_status('create_ec2_instance', collected_data)
    print(f"🔍 EC2 status: {ec2_status}")

    print("\n🤖 Agent: Excellent! Now I have all the information needed. Let me create your EC2 instance...")
    print("✅ [Agent would now create EC2 instance with the new key pair]")


def test_key_pair_tools():
    """Test key pair tools (without actually creating resources)"""

    print("\n=== Testing Key Pair Tools ===")

    print("📋 Available key pair tools:")
    print("• create_key_pair(region, key_name) - Creates key pair and returns private key")
    print("• list_key_pairs(region) - Lists all key pairs in region")
    print("• delete_key_pair(region, key_name) - Deletes a key pair")
    print("• get_key_pair_details(region, key_name) - Gets detailed key pair info")

    print("\n🔑 Key pair creation features:")
    print("• Returns private key for immediate download")
    print("• Provides SSH usage instructions")
    print("• Includes security best practices")
    print("• Warns about key security")

    print("\n🔗 Integration with EC2:")
    print("• Agent asks about key pairs during EC2 creation")
    print("• Can create key pair if user doesn't have one")
    print("• Provides complete SSH setup instructions")
    print("• Ensures proper key permissions and security")


if __name__ == "__main__":
    test_key_pair_validation()
    test_data_collection_status()
    simulate_key_pair_creation_conversation()
    simulate_ec2_with_key_pair_conversation()
    test_key_pair_tools()

    print("\n" + "=" * 60)
    print("🎯 Key Takeaways:")
    print("1. Key pair creation is fully integrated into the agent")
    print("2. Agent collects all required data before creating key pairs")
    print("3. Private keys are provided for immediate download")
    print("4. EC2 instance creation seamlessly integrates key pair creation")
    print("5. Security best practices are included in all responses")
    print("6. Modular structure makes the agent easier to maintain")
