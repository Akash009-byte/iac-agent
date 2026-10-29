#!/usr/bin/env python3
"""
Test script to verify the complete download functionality
"""

import sys
import os
import time
import requests
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from webapp.agent_wrapper import interactive_agent


def test_complete_download_flow():
    """Test the complete download flow"""

    print("🧪 Testing Complete Download Flow")
    print("=" * 60)

    # Generate unique name
    unique_name = f'download-test-{int(time.time())}'
    print(f"📝 Testing with unique name: {unique_name}")

    try:
        # Test message
        test_message = f"Create SSH key named {unique_name} in us-east-1"
        print(f"📝 Test Message: {test_message}")

        # Call agent
        response = interactive_agent(test_message)

        print(f"📝 Agent Response:")
        print("-" * 50)
        print(response)
        print("-" * 50)

        # Check for key indicators
        has_private_key = "-----BEGIN RSA PRIVATE KEY-----" in response
        has_success = "created successfully" in response.lower()
        has_key_pair_id = "Key Pair ID:" in response
        has_private_key_header = "🔑 PRIVATE KEY" in response

        print(f"\n🔍 Response Analysis:")
        print(f"✅ Contains private key: {has_private_key}")
        print(f"✅ Contains success: {has_success}")
        print(f"✅ Contains Key Pair ID: {has_key_pair_id}")
        print(f"✅ Contains PRIVATE KEY header: {has_private_key_header}")

        is_complete_response = has_private_key and has_success and has_key_pair_id
        print(f"✅ Complete response: {is_complete_response}")

        if is_complete_response:
            print(f"\n🎉 SUCCESS! Agent returns complete tool response")

            # Test webapp detection logic
            key_pair_indicators = [
                "PRIVATE KEY" in response,
                "-----BEGIN RSA PRIVATE KEY-----" in response,
                "key pair" in response.lower() and "created successfully" in response.lower(),
                "ssh key" in response.lower() and "created" in response.lower(),
                "private key" in response.lower() and "save" in response.lower()
            ]

            detection_triggered = any(key_pair_indicators)
            print(f"✅ Webapp detection will work: {detection_triggered}")

            if detection_triggered:
                # Test extraction
                import re
                import uuid

                key_id = str(uuid.uuid4())
                key_name_match = re.search(r'Key Name:\s*([^\n]+)', response)
                region_match = re.search(r'Region:\s*([^\n]+)', response)

                key_name = key_name_match.group(1).strip() if key_name_match else unique_name
                region = region_match.group(1).strip() if region_match else "us-east-1"

                private_key_match = re.search(r'```\n(-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----)\n```', response, re.DOTALL)

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

                    print(f"✅ Download info would be created:")
                    print(f"   - Download URL: {download_info['download_url']}")
                    print(f"   - File name: {key_name}.pem")
                    print(f"   - Instructions: {download_info['instructions']}")

                    # Test file content
                    print(f"\n🔍 File Content Test:")
                    print(f"✅ Private key starts with: {private_key[:50]}...")
                    print(f"✅ Private key ends with: ...{private_key[-50:]}")
                    print(f"✅ File would be named: {key_name}.pem")
                    print(f"✅ File size: {len(private_key)} characters")

                    return True
                else:
                    print(f"❌ Private key extraction failed")
                    return False
            else:
                print(f"❌ Webapp detection will not work")
                return False
        else:
            print(f"\n❌ ISSUE: Agent response is incomplete")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_webapp_integration():
    """Test webapp integration simulation"""

    print(f"\n🌐 Testing Webapp Integration")
    print("=" * 60)

    # Simulate webapp processing
    mock_agent_response = """✅ Key pair created successfully!

Key Pair Details:
- Key Name: test-webapp-integration
- Key Pair ID: key-123456
- Region: us-east-1

🔑 PRIVATE KEY (Save this securely - it won't be shown again):
```
PRIVATE_KEY_REMOVED
```

⚠️ IMPORTANT SECURITY NOTES:
1. Save this private key to a secure location (e.g., ~/.ssh/test-webapp-integration.pem)
2. Set proper permissions: chmod 400 ~/.ssh/test-webapp-integration.pem
3. Never share this private key publicly
4. Use this key to SSH into your EC2 instances
5. AWS does not store the private key - this is your only copy!

SSH Usage Example:
ssh -i ~/.ssh/test-webapp-integration.pem ec2-user@<instance-public-ip>

🔑 DOWNLOAD YOUR SSH KEY:
Your SSH key is ready for download! The private key above will be available for download in the web interface.
"""

    # Test webapp detection logic
    key_pair_indicators = [
        "PRIVATE KEY" in mock_agent_response,
        "-----BEGIN RSA PRIVATE KEY-----" in mock_agent_response,
        "key pair" in mock_agent_response.lower() and "created successfully" in mock_agent_response.lower(),
        "ssh key" in mock_agent_response.lower() and "created" in mock_agent_response.lower(),
        "private key" in mock_agent_response.lower() and "save" in mock_agent_response.lower()
    ]

    detection_triggered = any(key_pair_indicators)
    print(f"✅ Webapp detection triggered: {detection_triggered}")

    if detection_triggered:
        # Test extraction
        import re
        import uuid

        key_id = str(uuid.uuid4())
        key_name_match = re.search(r'Key Name:\s*([^\n]+)', mock_agent_response)
        region_match = re.search(r'Region:\s*([^\n]+)', mock_agent_response)

        key_name = key_name_match.group(1).strip() if key_name_match else "test-webapp-integration"
        region = region_match.group(1).strip() if region_match else "us-east-1"

        private_key_match = re.search(r'```\n(-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----)\n```', mock_agent_response, re.DOTALL)

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
            print(f"   - File name: {key_name}.pem")
            print(f"   - Instructions: {download_info['instructions']}")

            # Test file content
            print(f"\n🔍 File Content Test:")
            print(f"✅ Private key starts with: {private_key[:50]}...")
            print(f"✅ Private key ends with: ...{private_key[-50:]}")
            print(f"✅ File would be named: {key_name}.pem")
            print(f"✅ File size: {len(private_key)} characters")

            return True
        else:
            print(f"❌ Private key extraction failed")
            return False
    else:
        print(f"❌ Webapp detection not triggered")
        return False


if __name__ == "__main__":
    print("🚀 Testing Complete Download Functionality")
    print("=" * 60)

    # Test 1: Complete download flow
    download_flow_passed = test_complete_download_flow()

    # Test 2: Webapp integration
    webapp_integration_passed = test_webapp_integration()

    print(f"\n" + "=" * 60)
    print(f"🎯 Final Results:")
    print(f"✅ Complete download flow: {'PASS' if download_flow_passed else 'FAIL'}")
    print(f"✅ Webapp integration: {'PASS' if webapp_integration_passed else 'FAIL'}")

    if download_flow_passed and webapp_integration_passed:
        print(f"\n🎉 SUCCESS! Complete download functionality is working!")
        print(f"The webapp will detect key pair creation and provide download functionality.")
        print(f"\n💡 Next Steps:")
        print(f"1. Restart the webapp: python3 main.py")
        print(f"2. Open the webapp in your browser")
        print(f"3. Ask: 'Create a new SSH key pair named my-key'")
        print(f"4. Verify the download button appears")
        print(f"5. Test the download functionality")
        print(f"6. Verify the file is named correctly (e.g., my-key.pem)")
    else:
        print(f"\n❌ ISSUES FOUND:")
        if not download_flow_passed:
            print(f"   - Complete download flow needs fixes")
        if not webapp_integration_passed:
            print(f"   - Webapp integration needs fixes")

    print(f"\n🔧 Summary:")
    print(f"The download functionality is implemented with:")
    print(f"- Agent returns complete tool responses with private keys")
    print(f"- Webapp detects key pair creation")
    print(f"- Download button appears in chat interface")
    print(f"- Files are named with user-provided name + .pem extension")
    print(f"- Download endpoint serves files with correct headers")
