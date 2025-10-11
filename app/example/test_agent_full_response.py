#!/usr/bin/env python3
"""
Test script to verify the agent returns the complete tool response
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from webapp.agent_wrapper import interactive_agent


def test_agent_full_response():
    """Test that the agent returns the complete tool response"""
    
    print("🧪 Testing Agent Full Response")
    print("=" * 60)
    
    # Test message that should trigger key pair creation
    test_message = "Create a new SSH key pair named 'test-full-response' in us-east-1"
    
    try:
        print(f"📝 Test Message: {test_message}")
        print(f"🔄 Calling agent...")
        
        response = interactive_agent(test_message)
        
        print(f"📝 Agent Response:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
        # Check if response contains the complete tool output
        has_private_key_header = "🔑 PRIVATE KEY" in response
        has_begin_key = "-----BEGIN RSA PRIVATE KEY-----" in response
        has_end_key = "-----END RSA PRIVATE KEY-----" in response
        has_security_notes = "⚠️ IMPORTANT SECURITY NOTES" in response
        has_download_message = "🔑 DOWNLOAD YOUR SSH KEY" in response
        has_key_pair_id = "Key Pair ID:" in response
        
        print(f"\n🔍 Response Analysis:")
        print(f"✅ Contains '🔑 PRIVATE KEY': {has_private_key_header}")
        print(f"✅ Contains '-----BEGIN RSA PRIVATE KEY-----': {has_begin_key}")
        print(f"✅ Contains '-----END RSA PRIVATE KEY-----': {has_end_key}")
        print(f"✅ Contains '⚠️ IMPORTANT SECURITY NOTES': {has_security_notes}")
        print(f"✅ Contains '🔑 DOWNLOAD YOUR SSH KEY': {has_download_message}")
        print(f"✅ Contains 'Key Pair ID:': {has_key_pair_id}")
        
        # Check if it's a complete response
        is_complete_response = all([
            has_private_key_header,
            has_begin_key,
            has_end_key,
            has_security_notes,
            has_download_message,
            has_key_pair_id
        ])
        
        print(f"\n🎯 Complete Response: {is_complete_response}")
        
        if is_complete_response:
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
            print(f"This prevents the webapp from detecting and extracting the private key")
            
            # Check what's missing
            missing_parts = []
            if not has_private_key_header:
                missing_parts.append("PRIVATE KEY header")
            if not has_begin_key:
                missing_parts.append("BEGIN RSA PRIVATE KEY")
            if not has_end_key:
                missing_parts.append("END RSA PRIVATE KEY")
            if not has_security_notes:
                missing_parts.append("Security notes")
            if not has_download_message:
                missing_parts.append("Download message")
            if not has_key_pair_id:
                missing_parts.append("Key Pair ID")
            
            print(f"Missing parts: {', '.join(missing_parts)}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing agent response: {e}")
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
        has_private_key = "-----BEGIN RSA PRIVATE KEY-----" in response
        has_success = "created successfully" in response.lower()
        
        print(f"\n🔍 Detection Results:")
        print(f"✅ Contains private key: {has_private_key}")
        print(f"✅ Contains success message: {has_success}")
        
        is_complete = has_private_key and has_success
        print(f"✅ Complete response: {is_complete}")
        
        return is_complete
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Testing Agent Full Response")
    print("=" * 60)
    
    # Test 1: Full key creation
    full_test_passed = test_agent_full_response()
    
    # Test 2: Simple key creation
    simple_test_passed = test_simple_key_creation()
    
    print(f"\n" + "=" * 60)
    print(f"🎯 Final Results:")
    print(f"✅ Full key creation test: {'PASS' if full_test_passed else 'FAIL'}")
    print(f"✅ Simple key creation test: {'PASS' if simple_test_passed else 'FAIL'}")
    
    if full_test_passed and simple_test_passed:
        print(f"\n🎉 SUCCESS! Agent is working correctly!")
        print(f"The agent returns complete tool responses with private keys.")
        print(f"The webapp will be able to detect and provide download functionality.")
        print(f"\n💡 Next Steps:")
        print(f"1. Restart the webapp: python3 main.py")
        print(f"2. Test key pair creation in the webapp")
        print(f"3. Verify the download button appears")
    else:
        print(f"\n❌ ISSUES FOUND:")
        if not full_test_passed:
            print(f"   - Agent is not returning complete tool responses")
            print(f"   - The system prompt may need further updates")
        if not simple_test_passed:
            print(f"   - Simple key creation is not working")
        
        print(f"\n🔧 Debugging Steps:")
        print(f"1. Check the agent's system prompt")
        print(f"2. Verify the tool response format")
        print(f"3. Test with different message formats")
        print(f"4. Check the agent wrapper implementation")
    
    print(f"\n🔧 Summary:")
    print(f"The agent system prompt has been updated to explicitly require")
    print(f"returning the complete tool response without summarization.")
    print(f"This should enable the webapp to detect and extract private keys.")
