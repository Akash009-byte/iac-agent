#!/usr/bin/env python3
"""
Script to refresh AWS credentials and test them
"""

import boto3
import os
import json


def refresh_and_test_credentials():
    """Refresh AWS credentials and test them"""
    print("🔄 AWS Credential Refresh and Test")
    print("=" * 40)
    
    # Check current credentials
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_session_token = os.getenv('AWS_SESSION_TOKEN')
    aws_default_region = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
    
    print("📋 Current Credentials:")
    print(f"   AWS_ACCESS_KEY_ID: {'✅ Set' if aws_access_key_id else '❌ Not set'}")
    print(f"   AWS_SECRET_ACCESS_KEY: {'✅ Set' if aws_secret_access_key else '❌ Not set'}")
    print(f"   AWS_SESSION_TOKEN: {'✅ Set' if aws_session_token else '❌ Not set'}")
    print(f"   AWS_DEFAULT_REGION: {aws_default_region}")
    
    if aws_access_key_id:
        print(f"   Access Key (first 10 chars): {aws_access_key_id[:10]}...")
    
    if not aws_access_key_id or not aws_secret_access_key:
        print("\n❌ Missing required credentials!")
        print("Please set your credentials:")
        print("export AWS_ACCESS_KEY_ID=your_access_key")
        print("export AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("export AWS_SESSION_TOKEN=your_session_token")
        return False
    
    # Test 1: STS (Security Token Service)
    print("\n🧪 Test 1: STS (Security Token Service)")
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print("✅ STS test passed!")
        print(f"   Account: {identity['Account']}")
        print(f"   User/Role: {identity['Arn']}")
        print(f"   User ID: {identity['UserId']}")
    except Exception as e:
        print(f"❌ STS test failed: {e}")
        return False
    
    # Test 2: EC2 DescribeRegions
    print("\n🧪 Test 2: EC2 DescribeRegions")
    try:
        ec2 = boto3.client('ec2', region_name=aws_default_region)
        response = ec2.describe_regions()
        print(f"✅ EC2 DescribeRegions test passed!")
        print(f"   Available regions: {len(response['Regions'])}")
        print(f"   Test region ({aws_default_region}): {'✅ Available' if any(r['RegionName'] == aws_default_region for r in response['Regions']) else '❌ Not available'}")
    except Exception as e:
        print(f"❌ EC2 DescribeRegions test failed: {e}")
        return False
    
    # Test 3: EC2 DescribeInstances
    print("\n🧪 Test 3: EC2 DescribeInstances")
    try:
        ec2 = boto3.client('ec2', region_name=aws_default_region)
        response = ec2.describe_instances()
        instance_count = sum(len(reservation['Instances']) for reservation in response['Reservations'])
        print(f"✅ EC2 DescribeInstances test passed!")
        print(f"   Total instances: {instance_count}")
        
        if instance_count > 0:
            print("   Instance states:")
            states = {}
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    state = instance['State']['Name']
                    states[state] = states.get(state, 0) + 1
            
            for state, count in states.items():
                print(f"     {state}: {count}")
        
    except Exception as e:
        print(f"❌ EC2 DescribeInstances test failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Your credentials are working correctly.")
    return True


def suggest_fixes():
    """Suggest fixes for common credential issues"""
    print("\n💡 Common Fixes:")
    print("1. Session Token Expired:")
    print("   - Get new temporary credentials from AWS CLI or console")
    print("   - Run: aws sts get-session-token")
    
    print("\n2. Wrong Region:")
    print("   - Check if your resources are in a different region")
    print("   - Try: export AWS_DEFAULT_REGION=us-east-1")
    
    print("\n3. Insufficient Permissions:")
    print("   - Ensure your IAM user/role has EC2 permissions")
    print("   - Required: ec2:DescribeInstances, ec2:DescribeRegions")
    
    print("\n4. Invalid Credentials:")
    print("   - Double-check your access key and secret key")
    print("   - Ensure no extra spaces or characters")


if __name__ == "__main__":
    success = refresh_and_test_credentials()
    
    if not success:
        suggest_fixes()
    
    print("\n🚀 Next steps:")
    print("1. If tests passed: python app/iac/list_ec2_instances.py")
    print("2. If tests failed: Check the suggestions above")
    print("3. For the agent: python app/iac/agent.py")
