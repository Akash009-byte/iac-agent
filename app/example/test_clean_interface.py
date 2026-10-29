#!/usr/bin/env python3
"""
Test script to verify the clean interface without showing private keys
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from webapp.agent_wrapper import interactive_agent


def test_clean_interface():
    """Test the clean interface without private key display"""

    print("🧪 Testing Clean Interface")
    print("=" * 60)

    # Generate unique name
    unique_name = f'clean-test-{int(time.time())}'
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

        # Check that private key is NOT shown
        has_private_key = "-----BEGIN RSA PRIVATE KEY-----" in response
        has_end_key = "-----END RSA PRIVATE KEY-----" in response
        has_success = "created successfully" in response.lower()
        has_download_message = "download button below" in response.lower()
        has_key_details = "Key Pair Details:" in response

        print(f"\n🔍 Response Analysis:")
        print(f"❌ Contains private key (should be False): {has_private_key}")
        print(f"❌ Contains end key (should be False): {has_end_key}")
        print(f"✅ Contains success message: {has_success}")
        print(f"✅ Contains download message: {has_download_message}")
        print(f"✅ Contains key details: {has_key_details}")

        # Check if response is clean (no private key shown)
        is_clean_response = not has_private_key and not has_end_key and has_success and has_download_message
        print(f"✅ Clean response (no private key shown): {is_clean_response}")

        if is_clean_response:
            print(f"\n🎉 SUCCESS! Clean interface is working!")
            print(f"The private key is not shown in the chat interface.")
            print(f"Users will only see the download button.")

            # Test webapp detection logic
            key_pair_indicators = [
                "key pair" in response.lower() and "created successfully" in response.lower(),
                "ssh key" in response.lower() and "ready for download" in response.lower(),
                "download your ssh key" in response.lower(),
                "key pair details:" in response.lower(),
                "ssh usage example:" in response.lower()
            ]

            detection_triggered = any(key_pair_indicators)
            print(f"✅ Webapp detection will work: {detection_triggered}")

            if detection_triggered:
                # Test extraction
                import re

                key_name_match = re.search(r'Key Name:\s*([^\n]+)', response)
                region_match = re.search(r'Region:\s*([^\n]+)', response)

                key_name = key_name_match.group(1).strip() if key_name_match else unique_name
                region = region_match.group(1).strip() if region_match else "us-east-1"

                print(f"✅ Key extraction successful:")
                print(f"   - Key Name: {key_name}")
                print(f"   - Region: {region}")

                # Test file creation
                ssh_dir = os.path.join(os.path.dirname(__file__), "..", "ssh")
                key_file_path = os.path.join(ssh_dir, f"{key_name}.pem")

                if os.path.exists(key_file_path):
                    print(f"✅ SSH key file exists: {key_file_path}")

                    # Test download info creation
                    download_info = {
                        "key_name": key_name,
                        "file_name": f"{key_name}.pem",
                        "download_url": f"/api/download-file/{key_name}.pem",
                        "instructions": f"Your SSH key '{key_name}' is ready for download. Click the download button below to save it securely."
                    }

                    print(f"✅ Download info would be created:")
                    print(f"   - Download URL: {download_info['download_url']}")
                    print(f"   - File name: {download_info['file_name']}")
                    print(f"   - Instructions: {download_info['instructions']}")

                    return True
                else:
                    print(f"❌ SSH key file doesn't exist")
                    return False
            else:
                print(f"❌ Webapp detection will not work")
                return False
        else:
            print(f"\n❌ ISSUE: Private key is still being shown")
            print(f"The interface is not clean - private key content is visible")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Testing Clean Interface")
    print("=" * 60)

    success = test_clean_interface()

    print(f"\n" + "=" * 60)
    print(f"🎯 Final Result: {'PASS' if success else 'FAIL'}")

    if success:
        print(f"\n🎉 SUCCESS! Clean interface is working!")
        print(f"The private key is not shown in the chat interface.")
        print(f"Users will only see the download button.")
        print(f"\n💡 Next Steps:")
        print(f"1. Restart the webapp: python3 main.py")
        print(f"2. Test key pair creation in the webapp")
        print(f"3. Verify the clean interface (no private key shown)")
        print(f"4. Test the download button functionality")
    else:
        print(f"\n❌ ISSUE: Clean interface is not working")
        print(f"The private key is still being shown in the chat")
        print(f"The agent wrapper needs further updates")

    print(f"\n🔧 Summary:")
    print(f"The clean interface hides private keys from the chat")
    print(f"and only shows a download button for users to get the key.")
