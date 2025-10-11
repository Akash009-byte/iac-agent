#!/usr/bin/env python3
"""
Test script to debug the download button issue
"""

import sys
import os
import time
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from webapp.agent_wrapper import interactive_agent
from iac.interactive_strands_agent import interactive_agent as original_agent


def test_download_button_debug():
    """Debug the download button issue"""
    
    print("🧪 Testing Download Button Debug")
    print("=" * 60)
    
    # Generate unique name
    unique_name = f'debug-test-{int(time.time())}'
    print(f"📝 Testing with unique name: {unique_name}")
    
    try:
        # Test message
        test_message = f"Create SSH key named {unique_name} in us-east-1"
        print(f"📝 Test Message: {test_message}")
        
        # Get original agent response (with private key)
        print(f"📝 Getting original agent response...")
        original_response = original_agent(test_message)
        print(f"📝 Original response length: {len(str(original_response))}")
        print(f"📝 Original response preview: {str(original_response)[:300]}...")
        
        # Get cleaned response from wrapper
        print(f"📝 Getting cleaned response from wrapper...")
        cleaned_response = interactive_agent(test_message)
        print(f"📝 Cleaned response length: {len(cleaned_response)}")
        print(f"📝 Cleaned response preview: {cleaned_response[:300]}...")
        
        # Test webapp detection logic
        print(f"\n🔍 Testing Webapp Detection Logic:")
        
        # Enhanced detection patterns for key pair creation
        key_pair_indicators = [
            "key pair" in cleaned_response.lower() and "created successfully" in cleaned_response.lower(),
            "ssh key" in cleaned_response.lower() and "ready for download" in cleaned_response.lower(),
            "download your ssh key" in cleaned_response.lower(),
            "key pair details:" in cleaned_response.lower(),
            "ssh usage example:" in cleaned_response.lower(),
            "download button below" in cleaned_response.lower()
        ]
        
        print(f"   Contains 'key pair' + 'created successfully': {key_pair_indicators[0]}")
        print(f"   Contains 'ssh key' + 'ready for download': {key_pair_indicators[1]}")
        print(f"   Contains 'download your ssh key': {key_pair_indicators[2]}")
        print(f"   Contains 'key pair details:': {key_pair_indicators[3]}")
        print(f"   Contains 'ssh usage example:': {key_pair_indicators[4]}")
        print(f"   Contains 'download button below': {key_pair_indicators[5]}")
        
        detection_triggered = any(key_pair_indicators)
        print(f"✅ Detection triggered: {detection_triggered}")
        
        if detection_triggered:
            print(f"✅ Key pair creation detected!")
            
            # Test extraction
            import re
            
            # Extract key name from cleaned response
            key_name_patterns = [
                r'Key Name:\s*([^\n]+)',
                r'key pair named?\s*[\'"]?([^\s\'"\n]+)',
                r'key pair\s+[\'"]?([^\s\'"\n]+)',
                r'SSH key\s+[\'"]?([^\s\'"\n]+)',
                r'private key\s+[\'"]?([^\s\'"\n]+)'
            ]
            
            key_name = "ssh-key"
            for pattern in key_name_patterns:
                match = re.search(pattern, cleaned_response, re.IGNORECASE)
                if match:
                    key_name = match.group(1).strip()
                    break
            
            # Extract key pair ID
            key_pair_id_patterns = [
                r'Key Pair ID:\s*([^\n]+)',
                r'key pair id:\s*([^\n]+)',
                r'key-([a-f0-9]+)'
            ]
            
            key_pair_id = "unknown"
            for pattern in key_pair_id_patterns:
                match = re.search(pattern, cleaned_response, re.IGNORECASE)
                if match:
                    key_pair_id = match.group(1).strip()
                    break
            
            # Extract region
            region_patterns = [
                r'Region:\s*([^\n]+)',
                r'in\s+([a-z0-9-]+)',
                r'region\s+([a-z0-9-]+)'
            ]
            
            region = "us-east-1"
            for pattern in region_patterns:
                match = re.search(pattern, cleaned_response, re.IGNORECASE)
                if match:
                    region = match.group(1).strip()
                    break
            
            print(f"✅ Key extraction successful:")
            print(f"   - Key Name: {key_name}")
            print(f"   - Key Pair ID: {key_pair_id}")
            print(f"   - Region: {region}")
            
            # Test private key extraction from original response
            private_key_patterns = [
                r'```\n(-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----)\n```',
                r'```(-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----)```',
                r'(-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----)',
                r'PRIVATE KEY.*?\n(-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----)'
            ]
            
            private_key = None
            # Search in original response first, then cleaned response
            for response_text in [str(original_response), cleaned_response]:
                for pattern in private_key_patterns:
                    match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
                    if match:
                        private_key = match.group(1).strip()
                        break
                if private_key:
                    break
            
            if private_key:
                print(f"✅ Private key extracted successfully, length: {len(private_key)}")
                print(f"   Private key preview: {private_key[:100]}...")
                
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
                    
                    # Test WebSocket message format
                    websocket_message = {
                        "type": "message",
                        "role": "assistant",
                        "content": cleaned_response,
                        "timestamp": "2024-01-01T12:00:00",
                        "download_info": download_info
                    }
                    
                    print(f"✅ WebSocket message would include download_info: {download_info is not None}")
                    print(f"✅ WebSocket message preview: {json.dumps(websocket_message, indent=2)[:500]}...")
                    
                    return True
                    
                except Exception as file_error:
                    print(f"❌ Error saving SSH key to file: {file_error}")
                    return False
            else:
                print(f"❌ Private key content not found")
                print(f"   Searched in original response: {len(str(original_response))} chars")
                print(f"   Searched in cleaned response: {len(cleaned_response)} chars")
                return False
        else:
            print(f"❌ Key pair creation not detected")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Testing Download Button Debug")
    print("=" * 60)
    
    success = test_download_button_debug()
    
    print(f"\n" + "=" * 60)
    print(f"🎯 Final Result: {'PASS' if success else 'FAIL'}")
    
    if success:
        print(f"\n🎉 SUCCESS! Download button debug shows everything working!")
        print(f"The webapp should detect key pair creation and show download button.")
        print(f"\n💡 Next Steps:")
        print(f"1. Open the webapp: http://localhost:5001")
        print(f"2. Test key pair creation in the webapp")
        print(f"3. Check browser console for JavaScript errors")
        print(f"4. Verify the download button appears and is clickable")
    else:
        print(f"\n❌ ISSUE: Download button debug shows problems")
        print(f"Check the detection logic and extraction patterns")
        print(f"The webapp will not show download button for key pair creation")
    
    print(f"\n🔧 Summary:")
    print(f"The webapp should detect key pair creation and show a download button")
    print(f"for users to download their SSH keys securely.")
