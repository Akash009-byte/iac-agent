#!/usr/bin/env python3
"""
Test the complete key pair creation and download flow
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from iac.tools.key_pair_tools import create_key_pair
from webapp.agent_wrapper import interactive_agent


def test_key_pair_tool_directly():
    """Test the key pair tool directly"""

    print("🧪 Testing Key Pair Tool Directly")
    print("=" * 50)

    key_name = "test-direct-tool"
    region = "us-east-1"

    try:
        response = create_key_pair(region, key_name)

        print(f"📝 Tool Response:")
        print("-" * 30)
        print(response)
        print("-" * 30)

        # Check detection patterns
        has_private_key = "PRIVATE KEY" in response
        has_begin_key = "-----BEGIN RSA PRIVATE KEY-----" in response
        has_success = "key pair" in response.lower() and "created successfully" in response.lower()

        print(f"\n🔍 Detection Patterns:")
        print(f"✅ 'PRIVATE KEY': {has_private_key}")
        print(f"✅ '-----BEGIN RSA PRIVATE KEY-----': {has_begin_key}")
        print(f"✅ 'key pair' + 'created successfully': {has_success}")

        detection_works = (has_private_key and has_begin_key) or has_success
        print(f"✅ Detection will work: {detection_works}")

        return detection_works

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_agent_wrapper():
    """Test the agent wrapper with key pair creation"""

    print(f"\n🤖 Testing Agent Wrapper")
    print("=" * 50)

    # Test message that should trigger key pair creation
    test_message = "Create a new SSH key pair named 'test-agent-key' in us-east-1"

    try:
        print(f"📝 Test Message: {test_message}")

        response = interactive_agent(test_message)

        print(f"📝 Agent Response:")
        print("-" * 30)
        print(response)
        print("-" * 30)

        # Check detection patterns
        has_private_key = "PRIVATE KEY" in response
        has_begin_key = "-----BEGIN RSA PRIVATE KEY-----" in response
        has_success = "key pair" in response.lower() and "created successfully" in response.lower()

        print(f"\n🔍 Detection Patterns:")
        print(f"✅ 'PRIVATE KEY': {has_private_key}")
        print(f"✅ '-----BEGIN RSA PRIVATE KEY-----': {has_begin_key}")
        print(f"✅ 'key pair' + 'created successfully': {has_success}")

        detection_works = (has_private_key and has_begin_key) or has_success
        print(f"✅ Detection will work: {detection_works}")

        if detection_works:
            # Test extraction
            import re
            key_name_match = re.search(r'Key Name:\s*([^\n]+)', response)
            region_match = re.search(r'Region:\s*([^\n]+)', response)

            key_name = key_name_match.group(1).strip() if key_name_match else "unknown"
            region = region_match.group(1).strip() if region_match else "unknown"

            private_key_match = re.search(r'```\n(-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----)\n```', response, re.DOTALL)

            print(f"\n🔍 Extraction Results:")
            print(f"✅ Key name: {key_name}")
            print(f"✅ Region: {region}")
            print(f"✅ Private key extracted: {private_key_match is not None}")

            if private_key_match:
                private_key = private_key_match.group(1)
                print(f"✅ Private key length: {len(private_key)} characters")

        return detection_works

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_webapp_simulation():
    """Simulate the webapp processing"""

    print(f"\n🌐 Testing Webapp Simulation")
    print("=" * 50)

    # Simulate agent response
    mock_response = """✅ Key pair created successfully!

Key Pair Details:
- Key Name: test-webapp-sim
- Key Pair ID: key-123456
- Region: us-east-1

🔑 PRIVATE KEY (Save this securely - it won't be shown again):
```
PRIVATE_KEY_REMOVED
```

⚠️ IMPORTANT SECURITY NOTES:
1. Save this private key to a secure location (e.g., ~/.ssh/test-webapp-sim.pem)
2. Set proper permissions: chmod 400 ~/.ssh/test-webapp-sim.pem
3. Never share this private key publicly
4. Use this key to SSH into your EC2 instances
5. AWS does not store the private key - this is your only copy!

SSH Usage Example:
ssh -i ~/.ssh/test-webapp-sim.pem ec2-user@<instance-public-ip>

🔑 DOWNLOAD YOUR SSH KEY:
Your SSH key is ready for download! The private key above will be available for download in the web interface.
"""

    # Test webapp detection logic
    if ("PRIVATE KEY" in mock_response and "-----BEGIN RSA PRIVATE KEY-----" in mock_response) or \
       ("key pair" in mock_response.lower() and "created successfully" in mock_response.lower()):

        print(f"✅ Webapp detection triggered")

        # Test extraction
        import re
        import uuid

        key_id = str(uuid.uuid4())
        key_name_match = re.search(r'Key Name:\s*([^\n]+)', mock_response)
        region_match = re.search(r'Region:\s*([^\n]+)', mock_response)

        key_name = key_name_match.group(1).strip() if key_name_match else "ssh-key"
        region = region_match.group(1).strip() if region_match else "us-east-1"

        private_key_match = re.search(r'```\n(-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----)\n```', mock_response, re.DOTALL)

        if private_key_match:
            private_key = private_key_match.group(1)

            print(f"✅ Key extraction successful:")
            print(f"   - Key ID: {key_id}")
            print(f"   - Key Name: {key_name}")
            print(f"   - Region: {region}")
            print(f"   - Private Key Length: {len(private_key)} characters")

            # Simulate download info creation
            download_info = {
                "key_id": key_id,
                "key_name": key_name,
                "download_url": f"/api/download-key/{key_id}",
                "instructions": f"Your SSH key '{key_name}' is ready for download. Click the download button below to save it securely."
            }

            print(f"✅ Download info created:")
            print(f"   - Download URL: {download_info['download_url']}")
            print(f"   - Instructions: {download_info['instructions']}")

            return True
        else:
            print(f"❌ Private key extraction failed")
            return False
    else:
        print(f"❌ Webapp detection not triggered")
        return False


if __name__ == "__main__":
    print("🚀 Testing Complete Key Pair Flow")
    print("=" * 60)

    # Test 1: Direct tool
    tool_works = test_key_pair_tool_directly()

    # Test 2: Agent wrapper
    agent_works = test_agent_wrapper()

    # Test 3: Webapp simulation
    webapp_works = test_webapp_simulation()

    print(f"\n" + "=" * 60)
    print(f"🎯 Final Results:")
    print(f"✅ Key Pair Tool: {'PASS' if tool_works else 'FAIL'}")
    print(f"✅ Agent Wrapper: {'PASS' if agent_works else 'FAIL'}")
    print(f"✅ Webapp Simulation: {'PASS' if webapp_works else 'FAIL'}")

    if tool_works and agent_works and webapp_works:
        print(f"\n🎉 SUCCESS! Complete flow is working!")
        print(f"The key pair creation and download functionality is ready.")
        print(f"\n💡 Next Steps:")
        print(f"1. Restart the webapp: python3 main.py")
        print(f"2. Open the webapp in your browser")
        print(f"3. Ask: 'Create a new SSH key pair named my-key'")
        print(f"4. Verify the download button appears")
        print(f"5. Test the download functionality")
    else:
        print(f"\n❌ ISSUES FOUND:")
        if not tool_works:
            print(f"   - Key pair tool needs fixes")
        if not agent_works:
            print(f"   - Agent wrapper needs fixes")
        if not webapp_works:
            print(f"   - Webapp detection needs fixes")

    print(f"\n🔧 Summary:")
    print(f"The key pair tool has been updated to use boto3 directly,")
    print(f"same as your working example. This ensures consistent behavior")
    print(f"and proper private key generation for download functionality.")
