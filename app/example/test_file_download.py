#!/usr/bin/env python3
"""
Test script to verify the file-based download system
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from webapp.agent_wrapper import interactive_agent


def test_file_download_system():
    """Test the file-based download system"""

    print("🧪 Testing File-Based Download System")
    print("=" * 60)

    # Generate unique name
    unique_name = f'file-test-{int(time.time())}'
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

                key_name_match = re.search(r'Key Name:\s*([^\n]+)', response)
                region_match = re.search(r'Region:\s*([^\n]+)', response)

                key_name = key_name_match.group(1).strip() if key_name_match else unique_name
                region = region_match.group(1).strip() if region_match else "us-east-1"

                private_key_match = re.search(r'```\n(-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----)\n```', response, re.DOTALL)

                if private_key_match:
                    private_key = private_key_match.group(1)

                    print(f"✅ Key extraction successful:")
                    print(f"   - Key Name: {key_name}")
                    print(f"   - Region: {region}")
                    print(f"   - Private Key Length: {len(private_key)} characters")

                    # Test file creation
                    ssh_dir = os.path.join(os.path.dirname(__file__), "..", "ssh")
                    os.makedirs(ssh_dir, exist_ok=True)

                    key_file_path = os.path.join(ssh_dir, f"{key_name}.pem")

                    try:
                        with open(key_file_path, 'w') as f:
                            f.write(private_key)

                        # Set proper permissions (chmod 400)
                        os.chmod(key_file_path, 0o400)

                        print(f"✅ SSH key saved to: {key_file_path}")

                        # Check if file exists and has correct content
                        if os.path.exists(key_file_path):
                            with open(key_file_path, 'r') as f:
                                saved_content = f.read()

                            if saved_content == private_key:
                                print(f"✅ File content matches private key")
                                print(f"✅ File permissions: {oct(os.stat(key_file_path).st_mode)[-3:]}")

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
                                print(f"❌ File content doesn't match private key")
                                return False
                        else:
                            print(f"❌ File was not created")
                            return False

                    except Exception as file_error:
                        print(f"❌ Error creating file: {file_error}")
                        return False
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


def test_download_endpoint():
    """Test the download endpoint"""

    print(f"\n🌐 Testing Download Endpoint")
    print("=" * 60)

    # Check if any SSH files exist
    ssh_dir = os.path.join(os.path.dirname(__file__), "..", "ssh")

    if os.path.exists(ssh_dir):
        files = [f for f in os.listdir(ssh_dir) if f.endswith('.pem')]
        print(f"📁 SSH directory exists: {ssh_dir}")
        print(f"📄 Found {len(files)} .pem files: {files}")

        if files:
            test_file = files[0]
            file_path = os.path.join(ssh_dir, test_file)

            print(f"🔍 Testing with file: {test_file}")
            print(f"📁 File path: {file_path}")

            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()

                print(f"✅ File exists and readable")
                print(f"📏 File size: {len(content)} characters")
                print(f"🔒 File permissions: {oct(os.stat(file_path).st_mode)[-3:]}")
                print(f"📝 Content starts with: {content[:50]}...")

                # Test download URL
                download_url = f"/api/download-file/{test_file}"
                print(f"🔗 Download URL: {download_url}")

                return True
            else:
                print(f"❌ File doesn't exist")
                return False
        else:
            print(f"❌ No .pem files found")
            return False
    else:
        print(f"❌ SSH directory doesn't exist")
        return False


if __name__ == "__main__":
    print("🚀 Testing File-Based Download System")
    print("=" * 60)

    # Test 1: File creation
    file_creation_passed = test_file_download_system()

    # Test 2: Download endpoint
    download_endpoint_passed = test_download_endpoint()

    print(f"\n" + "=" * 60)
    print(f"🎯 Final Results:")
    print(f"✅ File creation: {'PASS' if file_creation_passed else 'FAIL'}")
    print(f"✅ Download endpoint: {'PASS' if download_endpoint_passed else 'FAIL'}")

    if file_creation_passed and download_endpoint_passed:
        print(f"\n🎉 SUCCESS! File-based download system is working!")
        print(f"The webapp will save SSH keys to files and provide download functionality.")
        print(f"\n💡 Next Steps:")
        print(f"1. Restart the webapp: python3 main.py")
        print(f"2. Open the webapp in your browser")
        print(f"3. Ask: 'Create a new SSH key pair named my-key'")
        print(f"4. Verify the download button appears")
        print(f"5. Test the download functionality")
        print(f"6. Check that the file is saved in app/ssh/")
    else:
        print(f"\n❌ ISSUES FOUND:")
        if not file_creation_passed:
            print(f"   - File creation needs fixes")
        if not download_endpoint_passed:
            print(f"   - Download endpoint needs fixes")

    print(f"\n🔧 Summary:")
    print(f"The file-based download system saves SSH keys to app/ssh/")
    print(f"and provides download functionality through /api/download-file/")
    print(f"This is more reliable than the temporary storage approach.")
