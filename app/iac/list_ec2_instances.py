#!/usr/bin/env python3
"""
Standalone boto3 script to list AWS EC2 instances
"""

import boto3
import os
from datetime import datetime
from typing import List, Dict, Any


def get_ec2_client(region: str = "us-west-2"):
    """
    Create EC2 client with credentials from environment variables
    
    Args:
        region: AWS region
    
    Returns:
        EC2 client instance
    """
    # Get credentials from environment variables
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_session_token = os.getenv('AWS_SESSION_TOKEN')
    
    # Validate that required credentials are present
    if not aws_access_key_id or not aws_secret_access_key:
        raise ValueError("AWS credentials not found in environment variables. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.")
    
    # Create session with credentials
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        region_name=region
    )
    
    return session.client('ec2', region_name=region)


def list_all_instances(region: str = "us-west-2") -> List[Dict[str, Any]]:
    """
    List all EC2 instances in the specified region
    
    Args:
        region: AWS region to query
    
    Returns:
        List of instance dictionaries
    """
    try:
        ec2 = get_ec2_client(region)
        
        # Get all instances
        response = ec2.describe_instances()
        
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_info = {
                    'InstanceId': instance['InstanceId'],
                    'InstanceType': instance['InstanceType'],
                    'State': instance['State']['Name'],
                    'LaunchTime': instance['LaunchTime'],
                    'PublicIpAddress': instance.get('PublicIpAddress', 'N/A'),
                    'PrivateIpAddress': instance.get('PrivateIpAddress', 'N/A'),
                    'ImageId': instance['ImageId'],
                    'KeyName': instance.get('KeyName', 'N/A'),
                    'VpcId': instance.get('VpcId', 'N/A'),
                    'SubnetId': instance.get('SubnetId', 'N/A'),
                    'SecurityGroups': [sg['GroupName'] for sg in instance.get('SecurityGroups', [])],
                    'Tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                }
                instances.append(instance_info)
        
        return instances
        
    except Exception as e:
        print(f"❌ Error listing instances: {e}")
        return []


def list_instances_by_state(region: str = "us-west-2", state: str = "running") -> List[Dict[str, Any]]:
    """
    List EC2 instances filtered by state
    
    Args:
        region: AWS region to query
        state: Instance state filter (running, stopped, pending, etc.)
    
    Returns:
        List of instance dictionaries
    """
    try:
        ec2 = get_ec2_client(region)
        
        # Filter by instance state
        response = ec2.describe_instances(
            Filters=[
                {
                    'Name': 'instance-state-name',
                    'Values': [state]
                }
            ]
        )
        
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_info = {
                    'InstanceId': instance['InstanceId'],
                    'InstanceType': instance['InstanceType'],
                    'State': instance['State']['Name'],
                    'LaunchTime': instance['LaunchTime'],
                    'PublicIpAddress': instance.get('PublicIpAddress', 'N/A'),
                    'PrivateIpAddress': instance.get('PrivateIpAddress', 'N/A'),
                    'ImageId': instance['ImageId'],
                    'KeyName': instance.get('KeyName', 'N/A'),
                    'VpcId': instance.get('VpcId', 'N/A'),
                    'SubnetId': instance.get('SubnetId', 'N/A'),
                    'SecurityGroups': [sg['GroupName'] for sg in instance.get('SecurityGroups', [])],
                    'Tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                }
                instances.append(instance_info)
        
        return instances
        
    except Exception as e:
        print(f"❌ Error listing instances by state: {e}")
        return []


def print_instances_table(instances: List[Dict[str, Any]], region: str):
    """
    Print instances in a formatted table
    
    Args:
        instances: List of instance dictionaries
        region: AWS region
    """
    if not instances:
        print(f"📋 No EC2 instances found in {region}")
        return
    
    print(f"📋 EC2 Instances in {region} ({len(instances)} instances)")
    print("=" * 120)
    print(f"{'Instance ID':<20} {'Type':<12} {'State':<10} {'Public IP':<15} {'Private IP':<15} {'Launch Time':<20}")
    print("-" * 120)
    
    for instance in instances:
        launch_time = instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S')
        print(f"{instance['InstanceId']:<20} {instance['InstanceType']:<12} {instance['State']:<10} "
              f"{instance['PublicIpAddress']:<15} {instance['PrivateIpAddress']:<15} {launch_time:<20}")


def print_instance_details(instances: List[Dict[str, Any]], region: str):
    """
    Print detailed information about instances
    
    Args:
        instances: List of instance dictionaries
        region: AWS region
    """
    if not instances:
        print(f"📋 No EC2 instances found in {region}")
        return
    
    print(f"📋 Detailed EC2 Instance Information for {region}")
    print("=" * 80)
    
    for i, instance in enumerate(instances, 1):
        print(f"\n{i}. Instance: {instance['InstanceId']}")
        print(f"   Type: {instance['InstanceType']}")
        print(f"   State: {instance['State']}")
        print(f"   AMI: {instance['ImageId']}")
        print(f"   Launch Time: {instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Public IP: {instance['PublicIpAddress']}")
        print(f"   Private IP: {instance['PrivateIpAddress']}")
        print(f"   Key Name: {instance['KeyName']}")
        print(f"   VPC ID: {instance['VpcId']}")
        print(f"   Subnet ID: {instance['SubnetId']}")
        print(f"   Security Groups: {', '.join(instance['SecurityGroups'])}")
        
        if instance['Tags']:
            print("   Tags:")
            for key, value in instance['Tags'].items():
                print(f"     {key}: {value}")


def validate_credentials():
    """Validate AWS credentials before proceeding"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        return True
        
    except Exception as e:
        print(f"❌ Credential validation failed: {e}")
        return False


def main():
    """Main function to demonstrate EC2 instance listing"""
    print("🚀 AWS EC2 Instance Listing Script")
    print("=" * 50)
    
    # Set region
    region = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
    print(f"🌍 Region: {region}")
    
    # Validate credentials first
    if not validate_credentials():
        return
    
    try:
        # Example 1: List all instances
        print("\n1. Listing all EC2 instances...")
        all_instances = list_all_instances(region)
        print_instances_table(all_instances, region)
        
        # Example 2: List running instances only
        print("\n2. Listing running instances only...")
        running_instances = list_instances_by_state(region, 'running')
        print_instances_table(running_instances, region)
        
        # Example 3: List stopped instances
        print("\n3. Listing stopped instances...")
        stopped_instances = list_instances_by_state(region, 'stopped')
        print_instances_table(stopped_instances, region)
        
        # Example 4: Detailed view of all instances
        print("\n4. Detailed instance information...")
        print_instance_details(all_instances, region)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure to set your AWS credentials:")
        print("   export AWS_ACCESS_KEY_ID=your_access_key")
        print("   export AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("   export AWS_DEFAULT_REGION=us-west-2")


if __name__ == "__main__":
    main()
