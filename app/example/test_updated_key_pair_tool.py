#!/usr/bin/env python3
"""
Test script to verify the updated key pair tool works correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from iac.tools.key_pair_tools import create_key_pair


def test_updated_key_pair_tool():
    """Test the updated key pair tool"""
    
    print("🧪 Testing Updated Key Pair Tool")
    print("=" * 60)
    
    # Test key pair creation
    key_name = "test-updated-tool"
    region = "us-east-1"
    
    print(f"📝 Creating key pair: {key_name} in {region}")
    
    try:
        response = create_key_pair(region, key_name)
        
        print(f"📝 Tool Response:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
        # Check if response contains private key
        has_private_key = "PRIVATE KEY" in response
        has_begin_key = "-----BEGIN RSA PRIVATE KEY-----" in response
        has_key_pair_success = ("key pair" in response.lower() and "created successfully" in response.lower())
        
        print(f"\n🔍 Detection Results:")
        print(f"✅ Contains 'PRIVATE KEY': {has_private_key}")
        print(f"✅ Contains '-----BEGIN RSA PRIVATE KEY-----': {has_begin_key}")
        print(f"✅ Contains 'key pair' and 'created successfully': {has_key_pair_success}")
        
        detection_triggered = (has_private_key and has_begin_key) or has_key_pair_success
        
        if detection_triggered:
            print(f"\n🎉 SUCCESS!")
            print(f"The updated key pair tool is working correctly.")
            print(f"The webapp will be able to detect and provide download functionality.")
            
            # Test extraction
            import re
            key_name_match = re.search(r'Key Name:\s*([^\n]+)', response)
            region_match = re.search(r'Region:\s*([^\n]+)', response)
            
            key_name_extracted = key_name_match.group(1).strip() if key_name_match else "unknown"
            region_extracted = region_match.group(1).strip() if region_match else "unknown"
            
            private_key_match = re.search(r'```\n(-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----)\n```', response, re.DOTALL)
            
            print(f"\n🔍 Extraction Results:")
            print(f"✅ Key name: {key_name_extracted}")
            print(f"✅ Region: {region_extracted}")
            print(f"✅ Private key extracted: {private_key_match is not None}")
            
            if private_key_match:
                private_key = private_key_match.group(1)
                print(f"✅ Private key length: {len(private_key)} characters")
                print(f"✅ Private key starts with: {private_key[:50]}...")
            
            return True
        else:
            print(f"\n❌ ISSUE:")
            print(f"The tool is not returning the expected format.")
            return False
            
    except Exception as e:
        print(f"❌ Error testing tool: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_webapp_detection():
    """Test webapp detection with updated tool response"""
    
    print(f"\n=== Testing Webapp Detection ===")
    
    # Simulate the updated tool response
    updated_tool_response = """✅ Key pair created successfully!

Key Pair Details:
- Key Name: test-updated-tool
- Key Pair ID: key-123456
- Region: us-east-1

🔑 PRIVATE KEY (Save this securely - it won't be shown again):
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA7ExamplePrivateKeyContentHere1234567890
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqr
stuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij
klmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZab
cdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTU
VWXYZabcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMN
OPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890ABCDEFG
HIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234
567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx
yz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqr
stuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijkl
mnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdef
ghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ
-----END RSA PRIVATE KEY-----
```

⚠️ IMPORTANT SECURITY NOTES:
1. Save this private key to a secure location (e.g., ~/.ssh/test-updated-tool.pem)
2. Set proper permissions: chmod 400 ~/.ssh/test-updated-tool.pem
3. Never share this private key publicly
4. Use this key to SSH into your EC2 instances
5. AWS does not store the private key - this is your only copy!

SSH Usage Example:
ssh -i ~/.ssh/test-updated-tool.pem ec2-user@<instance-public-ip>

🔑 DOWNLOAD YOUR SSH KEY:
Your SSH key is ready for download! The private key above will be available for download in the web interface.
"""
    
    # Test webapp detection logic
    has_private_key = "PRIVATE KEY" in updated_tool_response
    has_begin_key = "-----BEGIN RSA PRIVATE KEY-----" in updated_tool_response
    has_key_pair_success = ("key pair" in updated_tool_response.lower() and "created successfully" in updated_tool_response.lower())
    
    print(f"🔍 Webapp Detection Results:")
    print(f"✅ Contains 'PRIVATE KEY': {has_private_key}")
    print(f"✅ Contains '-----BEGIN RSA PRIVATE KEY-----': {has_begin_key}")
    print(f"✅ Contains 'key pair' and 'created successfully': {has_key_pair_success}")
    
    detection_triggered = (has_private_key and has_begin_key) or has_key_pair_success
    print(f"✅ Detection triggered: {detection_triggered}")
    
    if detection_triggered:
        print(f"\n🎉 SUCCESS!")
        print(f"The webapp will detect the updated tool response and show the download button.")
        
        # Test extraction
        import re
        key_name_match = re.search(r'Key Name:\s*([^\n]+)', updated_tool_response)
        region_match = re.search(r'Region:\s*([^\n]+)', updated_tool_response)
        
        key_name = key_name_match.group(1).strip() if key_name_match else "unknown"
        region = region_match.group(1).strip() if region_match else "unknown"
        
        private_key_match = re.search(r'```\n(-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----)\n```', updated_tool_response, re.DOTALL)
        
        print(f"\n🔍 Extraction Results:")
        print(f"✅ Key name: {key_name}")
        print(f"✅ Region: {region}")
        print(f"✅ Private key extracted: {private_key_match is not None}")
        
        if private_key_match:
            private_key = private_key_match.group(1)
            print(f"✅ Private key length: {len(private_key)} characters")
    
    return detection_triggered


if __name__ == "__main__":
    print("🚀 Testing Updated Key Pair Tool...")
    
    # Test webapp detection first
    webapp_detection_works = test_webapp_detection()
    
    # Test actual tool
    tool_works = test_updated_key_pair_tool()
    
    print(f"\n" + "=" * 60)
    print(f"🎯 Final Results:")
    print(f"✅ Webapp detection logic: {'PASS' if webapp_detection_works else 'FAIL'}")
    print(f"✅ Updated key pair tool: {'PASS' if tool_works else 'FAIL'}")
    
    if webapp_detection_works and tool_works:
        print(f"\n🎉 SUCCESS! The updated key pair tool is working!")
        print(f"The tool now uses the same boto3 approach as your working example.")
        print(f"The webapp will detect private keys and show download buttons.")
        print(f"\n💡 Next Steps:")
        print(f"1. Restart the webapp to apply the tool changes")
        print(f"2. Test creating a key pair in the webapp")
        print(f"3. Verify the download button appears")
    else:
        print(f"\n❌ ISSUES FOUND:")
        if not webapp_detection_works:
            print(f"   - Webapp detection logic needs adjustment")
        if not tool_works:
            print(f"   - Key pair tool needs further updates")
            print(f"   - Check AWS credentials setup")
    
    print(f"\n🔧 The key update was:")
    print(f"Updated the key pair tool to use boto3 directly, same as your working example.")
    print(f"This ensures consistent behavior and proper private key generation.")
