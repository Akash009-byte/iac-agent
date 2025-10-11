#!/usr/bin/env python3
"""
Standalone boto3 script to create AWS EC2 instances
"""

import boto3
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any, List


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


def get_latest_amazon_linux_ami(region: str = "us-west-2") -> str:
    """
    Get the latest Amazon Linux 2 AMI ID for the specified region
    
    Args:
        region: AWS region
    
    Returns:
        AMI ID string
    """
    try:
        ec2 = get_ec2_client(region)
        
        response = ec2.describe_images(
            Owners=['amazon'],
            Filters=[
                {'Name': 'name', 'Values': ['amzn2-ami-hvm-*']},
                {'Name': 'architecture', 'Values': ['x86_64']},
                {'Name': 'state', 'Values': ['available']}
            ]
        )
        
        # Sort by creation date to get the latest
        images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
        
        if images:
            latest_ami = images[0]
            print(f"✅ Found latest Amazon Linux 2 AMI: {latest_ami['ImageId']}")
            print(f"   Name: {latest_ami['Name']}")
            print(f"   Description: {latest_ami['Description']}")
            return latest_ami['ImageId']
        else:
            raise ValueError(f"No Amazon Linux 2 AMI found in {region}")
            
    except Exception as e:
        print(f"❌ Error getting Amazon Linux AMI: {e}")
        # Fallback to a known AMI ID
        fallback_ami = "ami-0c55b159cbfafe1f0"  # Amazon Linux 2 in us-west-2
        print(f"Using fallback AMI: {fallback_ami}")
        return fallback_ami


def create_security_group(region: str = "us-west-2", group_name: str = "default-sg") -> str:
    """
    Create a basic security group if it doesn't exist
    
    Args:
        region: AWS region
        group_name: Security group name
    
    Returns:
        Security group ID
    """
    try:
        ec2 = get_ec2_client(region)
        
        # Check if security group already exists
        try:
            response = ec2.describe_security_groups(GroupNames=[group_name])
            sg_id = response['SecurityGroups'][0]['GroupId']
            print(f"✅ Using existing security group: {sg_id}")
            return sg_id
        except ec2.exceptions.ClientError:
            pass  # Security group doesn't exist, create it
        
        # Get default VPC
        vpcs = ec2.describe_vpcs(Filters=[{'Name': 'is-default', 'Values': ['true']}])
        if not vpcs['Vpcs']:
            raise ValueError("No default VPC found")
        
        vpc_id = vpcs['Vpcs'][0]['VpcId']
        
        # Create security group
        response = ec2.create_security_group(
            GroupName=group_name,
            Description=f"Security group for {group_name}",
            VpcId=vpc_id
        )
        
        sg_id = response['GroupId']
        
        # Add SSH rule (port 22)
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }
            ]
        )
        
        print(f"✅ Created security group: {sg_id}")
        return sg_id
        
    except Exception as e:
        print(f"❌ Error creating security group: {e}")
        return None


def create_ec2_instance(
    region: str = "us-west-2",
    instance_type: str = "t2.micro",
    ami: Optional[str] = None,
    key_name: Optional[str] = None,
    security_group_ids: Optional[List[str]] = None,
    subnet_id: Optional[str] = None,
    user_data: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    min_count: int = 1,
    max_count: int = 1
) -> Dict[str, Any]:
    """
    Create an EC2 instance
    
    Args:
        region: AWS region
        instance_type: EC2 instance type
        ami: AMI ID (if None, uses latest Amazon Linux 2)
        key_name: SSH key pair name
        security_group_ids: List of security group IDs
        subnet_id: Subnet ID
        user_data: User data script
        tags: Dictionary of tags
        min_count: Minimum number of instances
        max_count: Maximum number of instances
    
    Returns:
        Dictionary with instance information
    """
    try:
        ec2 = get_ec2_client(region)
        
        # Get AMI if not provided
        if not ami:
            ami = get_latest_amazon_linux_ami(region)
        
        # Get security group if not provided
        if not security_group_ids:
            sg_id = create_security_group(region)
            if sg_id:
                security_group_ids = [sg_id]
        
        # Prepare launch parameters
        launch_params = {
            'ImageId': ami,
            'InstanceType': instance_type,
            'MinCount': min_count,
            'MaxCount': max_count
        }
        
        # Add optional parameters
        if key_name:
            launch_params['KeyName'] = key_name
        if security_group_ids:
            launch_params['SecurityGroupIds'] = security_group_ids
        if subnet_id:
            launch_params['SubnetId'] = subnet_id
        if user_data:
            launch_params['UserData'] = user_data
        
        print(f"🚀 Launching EC2 instance...")
        print(f"   Region: {region}")
        print(f"   Instance Type: {instance_type}")
        print(f"   AMI: {ami}")
        print(f"   Security Groups: {security_group_ids}")
        
        # Launch the instance
        response = ec2.run_instances(**launch_params)
        
        instances = response['Instances']
        instance_info = []
        
        for instance in instances:
            instance_id = instance['InstanceId']
            
            # Add tags if provided
            if tags:
                tag_list = [{'Key': k, 'Value': v} for k, v in tags.items()]
                ec2.create_tags(Resources=[instance_id], Tags=tag_list)
            
            instance_info.append({
                'InstanceId': instance_id,
                'InstanceType': instance_type,
                'State': instance['State']['Name'],
                'AMI': ami,
                'SecurityGroups': security_group_ids,
                'KeyName': key_name,
                'SubnetId': subnet_id
            })
            
            print(f"✅ Instance created: {instance_id}")
        
        return {
            'success': True,
            'instances': instance_info,
            'region': region
        }
        
    except Exception as e:
        print(f"❌ Error creating EC2 instance: {e}")
        return {
            'success': False,
            'error': str(e),
            'region': region
        }


def wait_for_instance_running(instance_id: str, region: str = "us-west-2", timeout: int = 300):
    """
    Wait for instance to be running
    
    Args:
        instance_id: Instance ID
        region: AWS region
        timeout: Timeout in seconds
    """
    try:
        ec2 = get_ec2_client(region)
        
        print(f"⏳ Waiting for instance {instance_id} to be running...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = ec2.describe_instances(InstanceIds=[instance_id])
            instance = response['Reservations'][0]['Instances'][0]
            state = instance['State']['Name']
            
            if state == 'running':
                print(f"✅ Instance {instance_id} is now running!")
                
                # Get instance details
                public_ip = instance.get('PublicIpAddress', 'N/A')
                private_ip = instance.get('PrivateIpAddress', 'N/A')
                
                print(f"   Public IP: {public_ip}")
                print(f"   Private IP: {private_ip}")
                return True
            elif state in ['stopped', 'terminated', 'shutting-down']:
                print(f"❌ Instance {instance_id} is in state: {state}")
                return False
            
            time.sleep(10)
        
        print(f"⏰ Timeout waiting for instance {instance_id}")
        return False
        
    except Exception as e:
        print(f"❌ Error waiting for instance: {e}")
        return False


def print_instance_summary(result: Dict[str, Any]):
    """
    Print a summary of created instances
    
    Args:
        result: Result dictionary from create_ec2_instance
    """
    if not result['success']:
        print(f"❌ Failed to create instances: {result['error']}")
        return
    
    instances = result['instances']
    region = result['region']
    
    print(f"\n📋 Instance Creation Summary for {region}")
    print("=" * 60)
    
    for i, instance in enumerate(instances, 1):
        print(f"{i}. Instance ID: {instance['InstanceId']}")
        print(f"   Type: {instance['InstanceType']}")
        print(f"   State: {instance['State']}")
        print(f"   AMI: {instance['AMI']}")
        print(f"   Security Groups: {', '.join(instance['SecurityGroups'])}")
        if instance['KeyName']:
            print(f"   Key Name: {instance['KeyName']}")
        if instance['SubnetId']:
            print(f"   Subnet ID: {instance['SubnetId']}")
        print()


def main():
    """Main function to demonstrate EC2 instance creation"""
    print("🚀 AWS EC2 Instance Creation Script")
    print("=" * 50)
    
    # Set region
    region = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
    print(f"🌍 Region: {region}")
    
    # Example 1: Create a basic t2.micro instance
    print("\n1. Creating a basic t2.micro instance...")
    result1 = create_ec2_instance(
        region=region,
        instance_type="t2.micro",
        tags={
            'Name': 'Basic-Instance',
            'Environment': 'Development',
            'CreatedBy': 'boto3-script'
        }
    )
    print_instance_summary(result1)
    
    # Example 2: Create a t3.small instance with custom configuration
    print("\n2. Creating a t3.small instance with custom config...")
    result2 = create_ec2_instance(
        region=region,
        instance_type="t3.small",
        tags={
            'Name': 'Custom-Instance',
            'Environment': 'Production',
            'Project': 'IaC-Demo'
        }
    )
    print_instance_summary(result2)
    
    # Example 3: Wait for first instance to be running
    if result1['success'] and result1['instances']:
        instance_id = result1['instances'][0]['InstanceId']
        wait_for_instance_running(instance_id, region)
    
    print("\n🎉 EC2 instance creation completed!")
    print("\n💡 Next steps:")
    print("1. Check instances: python app/iac/list_ec2_instances.py")
    print("2. SSH to instances (if key pair was specified)")
    print("3. Terminate instances when done to avoid charges")


if __name__ == "__main__":
    main()
