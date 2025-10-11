"""
Key Pair management tools for the IaC Agent
"""

import os
import base64
from typing import Optional
from strands import tool
from .validation import validate_key_pair_creation_params


def get_aws_client(service_name: str, region: str):
    """Create AWS client with credentials from environment variables"""
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_session_token = os.getenv('AWS_SESSION_TOKEN')
    
    if not aws_access_key_id or not aws_secret_access_key:
        raise ValueError("AWS credentials not found in environment variables.")
    
    import boto3
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        region_name=region
    )
    
    return session.client(service_name, region_name=region)


@tool
def create_key_pair(region: str, key_name: str) -> str:
    """Create a new EC2 key pair and return the private key for download"""
    # Validate required parameters
    is_valid, error_msg = validate_key_pair_creation_params(region, key_name)
    if not is_valid:
        return f"❌ {error_msg}. Please provide all required information before creating the key pair."
    
    try:
        # Use boto3 directly (same as working example)
        import boto3
        ec2 = boto3.client('ec2', region_name=region)
        
        # Create the key pair
        response = ec2.create_key_pair(KeyName=key_name)
        
        # Get the private key material
        private_key = response['KeyMaterial']
        key_pair_id = response['KeyPairId']
        
        return f"""✅ Key pair created successfully!

Key Pair Details:
- Key Name: {key_name}
- Key Pair ID: {key_pair_id}
- Region: {region}

🔑 PRIVATE KEY (Save this securely - it won't be shown again):
```
{private_key}
```

⚠️ IMPORTANT SECURITY NOTES:
1. Save this private key to a secure location (e.g., ~/.ssh/{key_name}.pem)
2. Set proper permissions: chmod 400 ~/.ssh/{key_name}.pem
3. Never share this private key publicly
4. Use this key to SSH into your EC2 instances
5. AWS does not store the private key - this is your only copy!

SSH Usage Example:
ssh -i ~/.ssh/{key_name}.pem ec2-user@<instance-public-ip>

🔑 DOWNLOAD YOUR SSH KEY:
Your SSH key is ready for download! The private key above will be available for download in the web interface.
"""
        
    except Exception as e:
        return f"❌ Error creating key pair: {str(e)}"


@tool
def list_key_pairs(region: str) -> str:
    """List all key pairs in the specified region"""
    try:
        # Use boto3 directly (same as working example)
        import boto3
        ec2 = boto3.client('ec2', region_name=region)
        
        response = ec2.describe_key_pairs()
        
        if not response['KeyPairs']:
            return f"No key pairs found in {region}"
        
        result = f"📋 Key Pairs in {region}:\n"
        for key_pair in response['KeyPairs']:
            result += f"""
- Key Name: {key_pair['KeyName']}
  Key Pair ID: {key_pair['KeyPairId']}
  Fingerprint: {key_pair['KeyFingerprint']}
  Type: {key_pair.get('KeyType', 'rsa')}
"""
        
        return result
        
    except Exception as e:
        return f"❌ Error listing key pairs: {str(e)}"


@tool
def delete_key_pair(region: str, key_name: str) -> str:
    """Delete a key pair"""
    try:
        # Use boto3 directly (same as working example)
        import boto3
        ec2 = boto3.client('ec2', region_name=region)
        
        # Delete the key pair
        ec2.delete_key_pair(KeyName=key_name)
        
        return f"""✅ Key pair deleted successfully!

Key Name: {key_name}
Region: {region}

Note: This only deletes the key pair from AWS. If you have the private key file locally, 
you should also delete it from your local system for security.
"""
        
    except Exception as e:
        return f"❌ Error deleting key pair: {str(e)}"


@tool
def get_key_pair_details(region: str, key_name: str) -> str:
    """Get detailed information about a specific key pair"""
    try:
        # Use boto3 directly (same as working example)
        import boto3
        ec2 = boto3.client('ec2', region_name=region)
        
        response = ec2.describe_key_pairs(KeyNames=[key_name])
        key_pair = response['KeyPairs'][0]
        
        return f"""📋 Key Pair Details:

Basic Information:
- Key Name: {key_pair['KeyName']}
- Key Pair ID: {key_pair['KeyPairId']}
- Fingerprint: {key_pair['KeyFingerprint']}
- Type: {key_pair.get('KeyType', 'rsa')}
- Region: {region}

Security Notes:
- Private key is not stored by AWS
- Keep your private key file secure
- Use chmod 400 for proper permissions
- Never share your private key

SSH Usage:
ssh -i ~/.ssh/{key_name}.pem ec2-user@<instance-public-ip>
"""
        
    except Exception as e:
        return f"❌ Error getting key pair details: {str(e)}"


@tool
def generate_ssh_key_file_content(key_name: str, private_key: str) -> str:
    """Generate SSH key file content for download"""
    try:
        # Create a properly formatted SSH key file
        ssh_key_content = f"""-----BEGIN RSA PRIVATE KEY-----
{private_key}
-----END RSA PRIVATE KEY-----"""
        
        return f"""📁 SSH Key File Content for {key_name}.pem:

{ssh_key_content}

📋 Instructions:
1. Save this content to a file named {key_name}.pem
2. Set proper permissions: chmod 400 {key_name}.pem
3. Use to SSH: ssh -i {key_name}.pem ec2-user@<instance-ip>
4. Keep this file secure and never share it

⚠️ Security Warning:
- This is your private key - keep it secure!
- AWS does not store this key
- Anyone with this key can access your instances
"""
        
    except Exception as e:
        return f"❌ Error generating SSH key file content: {str(e)}"
