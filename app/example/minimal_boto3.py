#!/usr/bin/env python3
"""
Minimal boto3 example for SSH key creation
Just the bare essentials
"""

import boto3
import os


def create_ssh_key(key_name, region='us-east-1'):
    """Create SSH key pair and save to file"""
    
    # Create EC2 client
    ec2 = boto3.client('ec2', region_name=region)
    
    # Create key pair
    response = ec2.create_key_pair(KeyName=key_name)
    
    # Get private key
    private_key = response['KeyMaterial']
    
    # Save to file
    filename = f"{key_name}.pem"
    with open(filename, 'w') as f:
        f.write(private_key)
    
    # Set permissions
    os.chmod(filename, 0o400)
    
    print(f"✅ SSH key created: {filename}")
    print(f"🔑 Use: ssh -i {filename} ec2-user@<instance-ip>")
    
    return filename


if __name__ == "__main__":
    # Create a key pair
    key_name = "my-key"
    filename = create_ssh_key(key_name)
    
    print(f"\n📁 File saved: {filename}")
    print(f"🔒 Permissions: chmod 400")
    print(f"💡 Ready to use with EC2 instances!")
