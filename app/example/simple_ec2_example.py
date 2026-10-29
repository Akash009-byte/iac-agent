#!/usr/bin/env python3
"""
Simple EC2 Instance Creation Example

A minimal example showing how to create an EC2 instance using boto3.
This is a simplified version for quick reference.
"""

import boto3
from botocore.exceptions import ClientError


def create_simple_instance():
    """Create a simple EC2 instance"""

    # Initialize EC2 client
    ec2 = boto3.client('ec2', region_name='us-east-1')

    try:
        # Create instance
        response = ec2.run_instances(
            ImageId='ami-0c02fb55956c7d316',  # Amazon Linux 2 AMI
            InstanceType='t2.micro',
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'Simple-Example-Instance'},
                        {'Key': 'Environment', 'Value': 'Development'}
                    ]
                }
            ]
        )

        # Get instance ID
        instance_id = response['Instances'][0]['InstanceId']
        print(f"✅ Instance created successfully: {instance_id}")

        # Wait for instance to be running
        print("⏳ Waiting for instance to be running...")
        waiter = ec2.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])

        # Get instance details
        response = ec2.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]

        print(f"📋 Instance Details:")
        print(f"   Instance ID: {instance['InstanceId']}")
        print(f"   Instance Type: {instance['InstanceType']}")
        print(f"   State: {instance['State']['Name']}")
        print(f"   Public IP: {instance.get('PublicIpAddress', 'N/A')}")
        print(f"   Private IP: {instance.get('PrivateIpAddress', 'N/A')}")
        print(f"   Launch Time: {instance['LaunchTime']}")

        return instance_id

    except ClientError as e:
        print(f"❌ Error creating instance: {e.response['Error']['Message']}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None


def terminate_instance(instance_id):
    """Terminate an EC2 instance"""

    ec2 = boto3.client('ec2', region_name='us-east-1')

    try:
        response = ec2.terminate_instances(InstanceIds=[instance_id])
        print(f"✅ Instance {instance_id} termination initiated")
        return True
    except ClientError as e:
        print(f"❌ Error terminating instance: {e.response['Error']['Message']}")
        return False


def list_instances():
    """List all instances"""

    ec2 = boto3.client('ec2', region_name='us-east-1')

    try:
        response = ec2.describe_instances()
        instances = []

        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append({
                    'id': instance['InstanceId'],
                    'type': instance['InstanceType'],
                    'state': instance['State']['Name'],
                    'public_ip': instance.get('PublicIpAddress'),
                    'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                })

        print(f"📋 Found {len(instances)} instances:")
        for instance in instances:
            name = instance['tags'].get('Name', 'Unnamed')
            print(f"   {instance['id']}: {name} ({instance['type']}) - {instance['state']}")

        return instances

    except ClientError as e:
        print(f"❌ Error listing instances: {e.response['Error']['Message']}")
        return []


if __name__ == "__main__":
    print("🚀 Simple EC2 Instance Creation Example")
    print("=" * 50)

    # Create instance
    instance_id = create_simple_instance()

    if instance_id:
        print("\n" + "=" * 50)

        # List instances
        print("📋 Listing all instances:")
        list_instances()

        print("\n" + "=" * 50)
        print("⚠️  Remember to terminate the instance when done to avoid charges!")
        print(f"   To terminate: terminate_instance('{instance_id}')")

        # Uncomment the next line to automatically terminate the instance
        # terminate_instance(instance_id)
