#!/usr/bin/env python3
"""
Example: Create EC2 Instance using boto3

This example demonstrates how to create an EC2 instance using boto3.
It includes error handling, instance configuration, and cleanup options.
"""

import boto3
import time
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional


class EC2InstanceManager:
    """Manages EC2 instance creation and operations"""

    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize EC2 client

        Args:
            region_name: AWS region name
        """
        self.ec2_client = boto3.client('ec2', region_name=region_name)
        self.region_name = region_name

    def create_instance(self,
                       image_id: str = 'ami-0c02fb55956c7d316',  # Amazon Linux 2 AMI
                       instance_type: str = 't2.micro',
                       key_name: Optional[str] = None,
                       security_group_ids: Optional[list] = None,
                       subnet_id: Optional[str] = None,
                       user_data: Optional[str] = None,
                       tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create an EC2 instance

        Args:
            image_id: AMI ID to use
            instance_type: Instance type (e.g., t2.micro, t3.small)
            key_name: Key pair name for SSH access
            security_group_ids: List of security group IDs
            subnet_id: Subnet ID for the instance
            user_data: User data script to run on instance startup
            tags: Dictionary of tags to apply to the instance

        Returns:
            Dictionary containing instance information
        """
        try:
            # Prepare instance parameters
            instance_params = {
                'ImageId': image_id,
                'InstanceType': instance_type,
                'MinCount': 1,
                'MaxCount': 1,
            }

            # Add optional parameters
            if key_name:
                instance_params['KeyName'] = key_name

            if security_group_ids:
                instance_params['SecurityGroupIds'] = security_group_ids

            if subnet_id:
                instance_params['SubnetId'] = subnet_id

            if user_data:
                instance_params['UserData'] = user_data

            # Create the instance
            print(f"Creating EC2 instance with parameters: {instance_params}")
            response = self.ec2_client.run_instances(**instance_params)

            # Get instance ID
            instance_id = response['Instances'][0]['InstanceId']
            print(f"Instance created successfully: {instance_id}")

            # Add tags if provided
            if tags:
                self.add_tags(instance_id, tags)

            # Wait for instance to be running
            print("Waiting for instance to be running...")
            waiter = self.ec2_client.get_waiter('instance_running')
            waiter.wait(InstanceIds=[instance_id])

            # Get instance details
            instance_details = self.get_instance_details(instance_id)

            return {
                'success': True,
                'instance_id': instance_id,
                'instance_details': instance_details,
                'message': f"Instance {instance_id} created successfully"
            }

        except ClientError as e:
            error_message = f"Error creating instance: {e.response['Error']['Message']}"
            print(error_message)
            return {
                'success': False,
                'error': error_message,
                'error_code': e.response['Error']['Code']
            }
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            print(error_message)
            return {
                'success': False,
                'error': error_message
            }

    def get_instance_details(self, instance_id: str) -> Dict[str, Any]:
        """Get detailed information about an instance"""
        try:
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            instance = response['Reservations'][0]['Instances'][0]

            return {
                'instance_id': instance['InstanceId'],
                'instance_type': instance['InstanceType'],
                'state': instance['State']['Name'],
                'public_ip': instance.get('PublicIpAddress'),
                'private_ip': instance.get('PrivateIpAddress'),
                'launch_time': instance['LaunchTime'].isoformat(),
                'image_id': instance['ImageId'],
                'vpc_id': instance.get('VpcId'),
                'subnet_id': instance.get('SubnetId'),
                'security_groups': instance.get('SecurityGroups', []),
                'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            }
        except ClientError as e:
            print(f"Error getting instance details: {e}")
            return {}

    def add_tags(self, instance_id: str, tags: Dict[str, str]):
        """Add tags to an instance"""
        try:
            tag_list = [{'Key': key, 'Value': value} for key, value in tags.items()]
            self.ec2_client.create_tags(Resources=[instance_id], Tags=tag_list)
            print(f"Tags added to instance {instance_id}: {tags}")
        except ClientError as e:
            print(f"Error adding tags: {e}")

    def terminate_instance(self, instance_id: str) -> Dict[str, Any]:
        """Terminate an instance"""
        try:
            response = self.ec2_client.terminate_instances(InstanceIds=[instance_id])
            print(f"Instance {instance_id} termination initiated")
            return {
                'success': True,
                'message': f"Instance {instance_id} termination initiated"
            }
        except ClientError as e:
            error_message = f"Error terminating instance: {e.response['Error']['Message']}"
            print(error_message)
            return {
                'success': False,
                'error': error_message
            }

    def list_instances(self, state: Optional[str] = None) -> list:
        """List instances, optionally filtered by state"""
        try:
            filters = []
            if state:
                filters.append({'Name': 'instance-state-name', 'Values': [state]})

            response = self.ec2_client.describe_instances(Filters=filters)
            instances = []

            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append(self.get_instance_details(instance['InstanceId']))

            return instances
        except ClientError as e:
            print(f"Error listing instances: {e}")
            return []


def main():
    """Example usage of EC2InstanceManager"""

    # Initialize the manager
    ec2_manager = EC2InstanceManager(region_name='us-east-1')

    # Example 1: Create a basic instance
    print("=== Example 1: Create Basic Instance ===")
    result = ec2_manager.create_instance(
        image_id='ami-0c02fb55956c7d316',  # Amazon Linux 2
        instance_type='t2.micro',
        tags={
            'Name': 'Example-Instance',
            'Environment': 'Development',
            'Project': 'EC2-Example'
        }
    )

    if result['success']:
        print(f"✅ {result['message']}")
        print(f"Instance ID: {result['instance_id']}")
        print(f"Public IP: {result['instance_details'].get('public_ip', 'N/A')}")
        print(f"Private IP: {result['instance_details'].get('private_ip', 'N/A')}")

        # Example 2: List running instances
        print("\n=== Example 2: List Running Instances ===")
        running_instances = ec2_manager.list_instances(state='running')
        print(f"Found {len(running_instances)} running instances:")
        for instance in running_instances:
            print(f"  - {instance['instance_id']}: {instance['instance_type']} ({instance['state']})")

        # Example 3: Terminate the instance (uncomment to actually terminate)
        # print("\n=== Example 3: Terminate Instance ===")
        # terminate_result = ec2_manager.terminate_instance(result['instance_id'])
        # if terminate_result['success']:
        #     print(f"✅ {terminate_result['message']}")

    else:
        print(f"❌ {result['error']}")


def create_instance_with_user_data():
    """Example with user data script"""

    ec2_manager = EC2InstanceManager()

    # User data script to install and start Apache
    user_data_script = """#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Hello from EC2!</h1>" > /var/www/html/index.html
"""

    result = ec2_manager.create_instance(
        image_id='ami-0c02fb55956c7d316',
        instance_type='t2.micro',
        user_data=user_data_script,
        tags={
            'Name': 'Web-Server-Instance',
            'Purpose': 'Web-Server',
            'Environment': 'Development'
        }
    )

    return result


def create_instance_in_vpc():
    """Example creating instance in a specific VPC subnet"""

    ec2_manager = EC2InstanceManager()

    # Note: You'll need to replace these with actual values from your AWS account
    result = ec2_manager.create_instance(
        image_id='ami-0c02fb55956c7d316',
        instance_type='t2.micro',
        subnet_id='subnet-12345678',  # Replace with actual subnet ID
        security_group_ids=['sg-12345678'],  # Replace with actual security group ID
        tags={
            'Name': 'VPC-Instance',
            'Environment': 'Production',
            'Network': 'Private'
        }
    )

    return result


if __name__ == "__main__":
    # Run the main example
    main()

    # Uncomment to run additional examples:
    # create_instance_with_user_data()
    # create_instance_in_vpc()
