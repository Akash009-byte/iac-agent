#!/usr/bin/env python3
"""
Test script to verify webapp key pair detection and download functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from webapp.agent_wrapper import interactive_agent


def test_webapp_key_detection():
    """Test webapp key pair detection with actual agent"""

    print("🧪 Testing Webapp Key Pair Detection")
    print("=" * 60)

    # Test message that should trigger key pair creation
    test_message = "Create a new SSH key pair named 'test-webapp-detection' in us-east-1"

    try:
        print(f"📝 Test Message: {test_message}")
        print(f"🔄 Calling agent...")

        response = interactive_agent(test_message)

        print(f"📝 Agent Response:")
        print("-" * 50)
        print(response)
        print("-" * 50)

        # Test webapp detection logic
        key_pair_indicators = [
            "PRIVATE KEY" in response,
            "-----BEGIN RSA PRIVATE KEY-----" in response,
            "key pair" in response.lower() and "created successfully" in response.lower(),
            "ssh key" in response.lower() and "created" in response.lower(),
            "private key" in response.lower() and "save" in response.lower()
        ]

        print(f"\n🔍 Webapp Detection Results:")
        print(f"✅ Contains 'PRIVATE KEY': {key_pair_indicators[0]}")
        print(f"✅ Contains '-----BEGIN RSA PRIVATE KEY-----': {key_pair_indicators[1]}")
        print(f"✅ Contains 'key pair' + 'created successfully': {key_pair_indicators[2]}")
        print(f"✅ Contains 'ssh key' + 'created': {key_pair_indicators[3]}")
        print(f"✅ Contains 'private key' + 'save': {key_pair_indicators[4]}")

        detection_triggered = any(key_pair_indicators)
        print(f"✅ Detection triggered: {detection_triggered}")

        if detection_triggered:
            print(f"\n🎉 SUCCESS! Webapp will detect key pair creation")

            # Test extraction
            import re
            key_name_patterns = [
                r'Key Name:\s*([^\n]+)',
                r'key pair named?\s*[\'"]?([^\s\'"\n]+)',
                r'key pair\s+[\'"]?([^\s\'"\n]+)',
                r'SSH key\s+[\'"]?([^\s\'"\n]+)',
                r'private key\s+[\'"]?([^\s\'"\n]+)'
            ]

            key_name = "ssh-key"
            for pattern in key_name_patterns:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    key_name = match.group(1).strip()
                    break

            region_patterns = [
                r'Region:\s*([^\n]+)',
                r'in\s+([a-z0-9-]+)',
                r'region\s+([a-z0-9-]+)'
            ]

            region = "us-east-1"
            for pattern in region_patterns:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    region = match.group(1).strip()
                    break

            private_key_patterns = [
                r'```\n(-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----)\n```',
                r'```(-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----)```',
                r'(-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----)',
                r'PRIVATE KEY.*?\n(-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----)'
            ]

            private_key = None
            for pattern in private_key_patterns:
                match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
                if match:
                    private_key = match.group(1).strip()
                    break

            print(f"\n🔍 Extraction Results:")
            print(f"✅ Key name: {key_name}")
            print(f"✅ Region: {region}")
            print(f"✅ Private key extracted: {private_key is not None}")

            if private_key:
                print(f"✅ Private key length: {len(private_key)} characters")
                print(f"✅ Private key starts with: {private_key[:50]}...")

                # Simulate download info creation
                import uuid
                key_id = str(uuid.uuid4())
                download_info = {
                    "key_id": key_id,
                    "key_name": key_name,
                    "download_url": f"/api/download-key/{key_id}",
                    "instructions": f"Your SSH key '{key_name}' is ready for download. Click the download button below to save it securely."
                }

                print(f"\n✅ Download info would be created:")
                print(f"   - Key ID: {key_id}")
                print(f"   - Download URL: {download_info['download_url']}")
                print(f"   - Instructions: {download_info['instructions']}")

                return True
            else:
                print(f"❌ Private key extraction failed")
                return False
        else:
            print(f"\n❌ ISSUE: Webapp will NOT detect key pair creation")
            print(f"The agent response doesn't contain the expected keywords")
            return False

    except Exception as e:
        print(f"❌ Error testing webapp detection: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simple_key_creation():
    """Test simple key creation message"""

    print(f"\n🧪 Testing Simple Key Creation")
    print("=" * 60)

    test_message = "Create SSH key named 'simple-test'"

    try:
        print(f"📝 Test Message: {test_message}")

        response = interactive_agent(test_message)

        print(f"📝 Agent Response:")
        print("-" * 30)
        print(response)
        print("-" * 30)

        # Check for key pair indicators
        has_private_key = "PRIVATE KEY" in response
        has_begin_key = "-----BEGIN RSA PRIVATE KEY-----" in response
        has_success = "key pair" in response.lower() and "created successfully" in response.lower()

        print(f"\n🔍 Detection Results:")
        print(f"✅ 'PRIVATE KEY': {has_private_key}")
        print(f"✅ '-----BEGIN RSA PRIVATE KEY-----': {has_begin_key}")
        print(f"✅ 'key pair' + 'created successfully': {has_success}")

        detection_works = (has_private_key and has_begin_key) or has_success
        print(f"✅ Detection will work: {detection_works}")

        return detection_works

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Testing Webapp Key Pair Detection")
    print("=" * 60)

    # Test 1: Full key creation
    full_test_passed = test_webapp_key_detection()

    # Test 2: Simple key creation
    simple_test_passed = test_simple_key_creation()

    print(f"\n" + "=" * 60)
    print(f"🎯 Final Results:")
    print(f"✅ Full key creation test: {'PASS' if full_test_passed else 'FAIL'}")
    print(f"✅ Simple key creation test: {'PASS' if simple_test_passed else 'FAIL'}")

    if full_test_passed and simple_test_passed:
        print(f"\n🎉 SUCCESS! Webapp detection is working!")
        print(f"The webapp will detect key pair creation and show download buttons.")
        print(f"\n💡 Next Steps:")
        print(f"1. Restart the webapp: python3 main.py")
        print(f"2. Open the webapp in your browser")
        print(f"3. Ask: 'Create a new SSH key pair named my-key'")
        print(f"4. Verify the download button appears")
        print(f"5. Test the download functionality")
    else:
        print(f"\n❌ ISSUES FOUND:")
        if not full_test_passed:
            print(f"   - Full key creation detection needs fixes")
        if not simple_test_passed:
            print(f"   - Simple key creation detection needs fixes")
        print(f"\n🔧 Debugging Steps:")
        print(f"1. Check the agent response format")
        print(f"2. Verify the detection patterns")
        print(f"3. Test with different message formats")

    print(f"\n🔧 Summary:")
    print(f"The webapp has been updated with enhanced detection patterns")
    print(f"and debug logging to better identify key pair creation responses.")
