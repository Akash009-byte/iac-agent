#!/usr/bin/env python3
"""
Simple script to test AWS credentials
"""

import boto3
import os


def test_credentials():
    """Test AWS credentials"""
    print("🔍 Testing AWS Credentials")
    print("=" * 30)
    
    # Check environment variables
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_session_token = os.getenv('AWS_SESSION_TOKEN')
    aws_default_region = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
    
    print(f"AWS_ACCESS_KEY_ID: {'✅ Set' if aws_access_key_id else '❌ Not set'}")
    print(f"AWS_SECRET_ACCESS_KEY: {'✅ Set' if aws_secret_access_key else '❌ Not set'}")
    print(f"AWS_SESSION_TOKEN: {'✅ Set' if aws_session_token else '❌ Not set'}")
    print(f"AWS_DEFAULT_REGION: {aws_default_region}")
    
    if aws_access_key_id:
        print(f"Access Key (first 10 chars): {aws_access_key_id[:10]}...")
    
    if not aws_access_key_id or not aws_secret_access_key:
        print("\n❌ Missing required credentials!")
        print("Please set:")
        print("export AWS_ACCESS_KEY_ID=your_access_key")
        print("export AWS_SECRET_ACCESS_KEY=your_secret_key")
        return False
    
    try:
        # Test credentials with STS
        print("\n🧪 Testing credentials with STS...")
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print("✅ Credentials are valid!")
        print(f"Account: {identity['Account']}")
        print(f"User/Role: {identity['Arn']}")
        
        # Test EC2 access
        print("\n🧪 Testing EC2 access...")
        ec2 = boto3.client('ec2', region_name=aws_default_region)
        response = ec2.describe_regions()
        print(f"✅ EC2 access successful! Found {len(response['Regions'])} regions")
        
        return True
        
    except Exception as e:
        print(f"❌ Credential test failed: {e}")
        return False


if __name__ == "__main__":
    test_credentials()
