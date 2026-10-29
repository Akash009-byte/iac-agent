#!/usr/bin/env python3
"""
Test script with unique key name
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from webapp.agent_wrapper import interactive_agent


def test_unique_key():
    """Test with unique key name"""

    # Generate unique name
    unique_name = f'test-{int(time.time())}'
    print(f"🧪 Testing with unique name: {unique_name}")
    print("=" * 60)

    try:
        # Test message
        test_message = f"Create SSH key named {unique_name}"
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

        print(f"\n🔍 Detection Results:")
        print(f"✅ Contains private key: {has_private_key}")
        print(f"✅ Contains success: {has_success}")
        print(f"✅ Contains Key Pair ID: {has_key_pair_id}")
        print(f"✅ Contains PRIVATE KEY header: {has_private_key_header}")

        is_complete = has_private_key and has_success and has_key_pair_id
        print(f"✅ Complete response: {is_complete}")

        if is_complete:
            print(f"\n🎉 SUCCESS! Agent returns complete tool response")
            print(f"The webapp will be able to detect and extract the private key")

            # Test webapp detection
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
                private_key_match = re.search(r'```\n(-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----)\n```', response, re.DOTALL)

                if private_key_match:
                    private_key = private_key_match.group(1)
                    print(f"✅ Private key extraction successful")
                    print(f"✅ Private key length: {len(private_key)} characters")
                    print(f"✅ Private key starts with: {private_key[:50]}...")

                    return True
                else:
                    print(f"❌ Private key extraction failed")
                    return False
            else:
                print(f"❌ Webapp detection will not work")
                return False
        else:
            print(f"\n❌ ISSUE: Agent response is incomplete")
            print(f"The agent is not returning the complete tool response")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Testing Unique Key Creation")
    print("=" * 60)

    success = test_unique_key()

    print(f"\n" + "=" * 60)
    print(f"🎯 Final Result: {'PASS' if success else 'FAIL'}")

    if success:
        print(f"\n🎉 SUCCESS! Agent is working correctly!")
        print(f"The agent returns complete tool responses with private keys.")
        print(f"The webapp will be able to detect and provide download functionality.")
        print(f"\n💡 Next Steps:")
        print(f"1. Restart the webapp: python3 main.py")
        print(f"2. Test key pair creation in the webapp")
        print(f"3. Verify the download button appears")
    else:
        print(f"\n❌ ISSUE: Agent is still not returning complete responses")
        print(f"The agent wrapper may need further updates")
        print(f"Or the agent system prompt needs to be more explicit")

    print(f"\n🔧 Summary:")
    print(f"Testing with unique key name to avoid conflicts")
    print(f"and verify the agent returns complete tool responses.")
