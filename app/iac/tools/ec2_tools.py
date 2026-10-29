"""
EC2 instance management tools for the IaC Agent
"""

import os
from datetime import datetime
from typing import Optional
from strands import tool
from .validation import validate_ec2_creation_params


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
def get_available_regions() -> str:
    """Get list of available AWS regions"""
    try:
        ec2 = get_aws_client("ec2", "us-east-1")
        response = ec2.describe_regions()
        regions = [region['RegionName'] for region in response['Regions']]
        regions_list = ", ".join(sorted(regions))
        return f"Available AWS regions: {regions_list}"
    except Exception as e:
        return f"Error getting regions: {str(e)}"


@tool
def get_instance_type_info(instance_type: str) -> str:
    """Get information about a specific EC2 instance type"""
    try:
        ec2 = get_aws_client("ec2", "us-east-1")
        response = ec2.describe_instance_types(InstanceTypes=[instance_type])

        if response['InstanceTypes']:
            instance_info = response['InstanceTypes'][0]
            return f"""Instance Type: {instance_type}
vCPUs: {instance_info['VCpuInfo']['DefaultVCpus']}
Memory: {instance_info['MemoryInfo']['SizeInMiB']} MiB
Network Performance: {instance_info['NetworkInfo']['NetworkPerformance']}
Storage: {instance_info.get('InstanceStorageInfo', {}).get('TotalSizeInGB', 'EBS only')} GB
Price: Check AWS Pricing Calculator for current rates"""
        else:
            return f"Instance type {instance_type} not found"
    except Exception as e:
        return f"Error getting instance type info: {str(e)}"


@tool
def get_latest_amazon_linux_ami(region: str) -> str:
    """Get the latest Amazon Linux 2 AMI ID for the specified region"""
    try:
        ec2 = get_aws_client("ec2", region)
        response = ec2.describe_images(
            Owners=['amazon'],
            Filters=[
                {'Name': 'name', 'Values': ['amzn2-ami-hvm-*']},
                {'Name': 'architecture', 'Values': ['x86_64']},
                {'Name': 'state', 'Values': ['available']}
            ]
        )

        images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
        if images:
            latest_ami = images[0]
            return f"""Latest Amazon Linux 2 AMI:
AMI ID: {latest_ami['ImageId']}
Name: {latest_ami['Name']}
Description: {latest_ami['Description']}
Architecture: {latest_ami['Architecture']}
Creation Date: {latest_ami['CreationDate']}"""
        else:
            return f"No Amazon Linux 2 AMI found in {region}"
    except Exception as e:
        return f"Error getting AMI: {str(e)}"


@tool
def create_ec2_instance(
    region: str,
    instance_type: str,
    instance_name: str,
    ami_id: Optional[str] = None,
    key_name: Optional[str] = None,
    security_group_ids: Optional[str] = None,
    subnet_id: Optional[str] = None,
    user_data: Optional[str] = None
) -> str:
    """Create an EC2 instance with the specified parameters"""
    # Validate required parameters (ami_id is now optional)
    is_valid, error_msg = validate_ec2_creation_params(region, instance_type, instance_name, ami_id or "default")
    if not is_valid:
        return f"❌ {error_msg}. Please provide all required information before creating the instance."

    try:
        ec2 = get_aws_client("ec2", region)

        # Use provided AMI ID or get latest Amazon Linux AMI as default
        if not ami_id:
            # Get latest Amazon Linux AMI as default
            ami_response = ec2.describe_images(
                Owners=['amazon'],
                Filters=[
                    {'Name': 'name', 'Values': ['amzn2-ami-hvm-*']},
                    {'Name': 'architecture', 'Values': ['x86_64']},
                    {'Name': 'state', 'Values': ['available']}
                ]
            )

            images = sorted(ami_response['Images'], key=lambda x: x['CreationDate'], reverse=True)
            ami_id = images[0]['ImageId'] if images else "ami-0c55b159cbfafe1f0"
            print(f"🔍 Using default Amazon Linux AMI: {ami_id}")
        else:
            print(f"🔍 Using provided AMI: {ami_id}")

        # Prepare launch parameters
        launch_params = {
            'ImageId': ami_id,
            'InstanceType': instance_type,
            'MinCount': 1,
            'MaxCount': 1,
            'TagSpecifications': [{
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': instance_name},
                    {'Key': 'Environment', 'Value': 'Development'},
                    {'Key': 'CreatedBy', 'Value': 'Strands-Agent'},
                    {'Key': 'CreatedDate', 'Value': datetime.now().strftime('%Y-%m-%d')}
                ]
            }]
        }

        # Add optional parameters
        if key_name:
            launch_params['KeyName'] = key_name
        if security_group_ids:
            launch_params['SecurityGroupIds'] = [sg.strip() for sg in security_group_ids.split(',')]
        if subnet_id:
            launch_params['SubnetId'] = subnet_id
        if user_data:
            launch_params['UserData'] = user_data

        # Launch the instance
        response = ec2.run_instances(**launch_params)
        instance = response['Instances'][0]

        return f"""✅ EC2 instance created successfully!

Instance Details:
- Instance ID: {instance['InstanceId']}
- Name: {instance_name}
- Type: {instance_type}
- AMI: {ami_id}
- Region: {region}
- State: {instance['State']['Name']}
- Key Pair: {key_name or 'None'}
- Security Groups: {security_group_ids or 'Default'}

🔄 The instance is starting up. It may take a few minutes to be fully running.
You can check the status using the list_ec2_instances tool.
"""

    except Exception as e:
        return f"❌ Error creating EC2 instance: {str(e)}"


@tool
def list_ec2_instances(region: str, state: Optional[str] = None) -> str:
    """List EC2 instances in the specified region"""
    try:
        ec2 = get_aws_client("ec2", region)

        filters = []
        if state:
            filters.append({'Name': 'instance-state-name', 'Values': [state]})

        response = ec2.describe_instances(Filters=filters)

        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                # Get instance name from tags
                instance_name = "N/A"
                if 'Tags' in instance:
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            instance_name = tag['Value']
                            break

                instances.append({
                    'InstanceId': instance['InstanceId'],
                    'InstanceType': instance['InstanceType'],
                    'State': instance['State']['Name'],
                    'Name': instance_name,
                    'PublicIp': instance.get('PublicIpAddress', 'N/A'),
                    'PrivateIp': instance.get('PrivateIpAddress', 'N/A'),
                    'LaunchTime': instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S')
                })

        if not instances:
            return f"No EC2 instances found in {region}" + (f" with state '{state}'" if state else "")

        result = f"📋 EC2 Instances in {region}:\n"
        for instance in instances:
            result += f"""
- Instance ID: {instance['InstanceId']}
  Name: {instance['Name']}
  Type: {instance['InstanceType']}
  State: {instance['State']}
  Public IP: {instance['PublicIp']}
  Private IP: {instance['PrivateIp']}
  Launched: {instance['LaunchTime']}
"""

        return result

    except Exception as e:
        return f"❌ Error listing EC2 instances: {str(e)}"


@tool
def terminate_ec2_instance(region: str, instance_id: str) -> str:
    """Terminate an EC2 instance"""
    try:
        ec2 = get_aws_client("ec2", region)

        # Get instance details before termination
        response = ec2.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]
        instance_name = "N/A"
        if 'Tags' in instance:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                    break

        # Terminate the instance
        ec2.terminate_instances(InstanceIds=[instance_id])

        return f"""✅ EC2 instance terminated successfully!

Instance Details:
- Instance ID: {instance_id}
- Name: {instance_name}
- Region: {region}

⚠️ WARNING: This action is irreversible! The instance and its data have been permanently deleted.
"""

    except Exception as e:
        return f"❌ Error terminating EC2 instance: {str(e)}"


@tool
def stop_ec2_instance(region: str, instance_id: str) -> str:
    """Stop a running EC2 instance"""
    try:
        ec2 = get_aws_client("ec2", region)

        # Get instance details before stopping
        response = ec2.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]
        instance_name = "N/A"
        if 'Tags' in instance:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                    break

        # Stop the instance
        ec2.stop_instances(InstanceIds=[instance_id])

        return f"""✅ EC2 instance stopped successfully!

Instance Details:
- Instance ID: {instance_id}
- Name: {instance_name}
- Region: {region}

💡 Note: The instance can be restarted using the start_ec2_instance tool.
"""

    except Exception as e:
        return f"❌ Error stopping EC2 instance: {str(e)}"


@tool
def start_ec2_instance(region: str, instance_id: str) -> str:
    """Start a stopped EC2 instance"""
    try:
        ec2 = get_aws_client("ec2", region)

        # Get instance details before starting
        response = ec2.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]
        instance_name = "N/A"
        if 'Tags' in instance:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                    break

        # Start the instance
        response = ec2.start_instances(InstanceIds=[instance_id])
        started_instance = response['StartingInstances'][0]

        return f"""✅ EC2 instance started successfully!

Instance Details:
- Instance ID: {instance_id}
- Name: {instance_name}
- Region: {region}
- Previous State: {started_instance['PreviousState']['Name']}
- Current State: {started_instance['CurrentState']['Name']}

🔄 The instance is starting up. It may take a few minutes to be fully running."""

    except Exception as e:
        return f"❌ Error starting EC2 instance: {str(e)}"


@tool
def reboot_ec2_instance(region: str, instance_id: str) -> str:
    """Reboot an EC2 instance"""
    try:
        ec2 = get_aws_client("ec2", region)

        # Get instance details before reboot
        response = ec2.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]
        instance_name = "N/A"
        if 'Tags' in instance:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                    break

        # Reboot the instance
        ec2.reboot_instances(InstanceIds=[instance_id])

        return f"""✅ EC2 instance rebooted successfully!

Instance Details:
- Instance ID: {instance_id}
- Name: {instance_name}
- Region: {region}

Note: The instance will restart and may be briefly unavailable during the reboot process.
"""

    except Exception as e:
        return f"❌ Error rebooting EC2 instance: {str(e)}"
