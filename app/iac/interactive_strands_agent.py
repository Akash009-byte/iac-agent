#!/usr/bin/env python3
"""
Interactive Strands-based IaC Agent for EC2 Instance Creation
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
from strands import Agent, tool
from strands.models.openai import OpenAIModel
import boto3


def get_aws_client(service_name: str, region: str):
    """Create AWS client with credentials from environment variables"""
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_session_token = os.getenv('AWS_SESSION_TOKEN')
    
    if not aws_access_key_id or not aws_secret_access_key:
        raise ValueError("AWS credentials not found in environment variables.")
    
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        region_name=region
    )
    
    return session.client(service_name, region_name=region)


def validate_required_params(params: dict, required_fields: list) -> tuple[bool, str]:
    """
    Validate that all required parameters are provided
    
    Args:
        params: Dictionary of parameters to validate
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    missing_fields = []
    for field in required_fields:
        if field not in params or params[field] is None or params[field] == "":
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required parameters: {', '.join(missing_fields)}"
    
    return True, ""


def validate_ec2_creation_params(region: str, instance_type: str, instance_name: str) -> tuple[bool, str]:
    """Validate EC2 instance creation parameters"""
    required_fields = ['region', 'instance_type', 'instance_name']
    params = {
        'region': region,
        'instance_type': instance_type,
        'instance_name': instance_name
    }
    return validate_required_params(params, required_fields)


def validate_security_group_creation_params(region: str, group_name: str, description: str) -> tuple[bool, str]:
    """Validate security group creation parameters"""
    required_fields = ['region', 'group_name', 'description']
    params = {
        'region': region,
        'group_name': group_name,
        'description': description
    }
    return validate_required_params(params, required_fields)


def validate_rule_addition_params(region: str, security_group_id: str, protocol: str, port: int, ip_range: str) -> tuple[bool, str]:
    """Validate security group rule addition parameters"""
    required_fields = ['region', 'security_group_id', 'protocol', 'port', 'ip_range']
    params = {
        'region': region,
        'security_group_id': security_group_id,
        'protocol': protocol,
        'port': port,
        'ip_range': ip_range
    }
    return validate_required_params(params, required_fields)


@tool
def get_data_collection_status(operation: str, collected_data: dict) -> str:
    """
    Check what information has been collected for an operation
    
    Args:
        operation: The operation being performed (e.g., 'create_ec2_instance', 'create_security_group')
        collected_data: Dictionary of data collected so far
        
    Returns:
        Status of data collection with missing fields
    """
    required_fields = {
        'create_ec2_instance': ['region', 'instance_type', 'instance_name'],
        'create_security_group': ['region', 'group_name', 'description'],
        'add_inbound_rule': ['region', 'security_group_id', 'protocol', 'port', 'source_ip'],
        'add_outbound_rule': ['region', 'security_group_id', 'protocol', 'port', 'destination_ip']
    }
    
    if operation not in required_fields:
        return f"Unknown operation: {operation}"
    
    missing_fields = []
    for field in required_fields[operation]:
        if field not in collected_data or collected_data[field] is None or collected_data[field] == "":
            missing_fields.append(field)
    
    if not missing_fields:
        return f"✅ All required data collected for {operation}. Ready to proceed!"
    else:
        return f"❌ Missing required fields for {operation}: {', '.join(missing_fields)}. Please collect these before proceeding."


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
    key_name: Optional[str] = None,
    security_group_ids: Optional[str] = None,
    subnet_id: Optional[str] = None,
    user_data: Optional[str] = None
) -> str:
    """Create an EC2 instance with the specified parameters"""
    # Validate required parameters
    is_valid, error_msg = validate_ec2_creation_params(region, instance_type, instance_name)
    if not is_valid:
        return f"❌ {error_msg}. Please provide all required information before creating the instance."
    
    try:
        ec2 = get_aws_client("ec2", region)
        
        # Get latest Amazon Linux AMI
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
        instance_id = instance['InstanceId']
        
        return f"""✅ Successfully created EC2 instance!
Instance ID: {instance_id}
Region: {region}
Instance Type: {instance_type}
Instance Name: {instance_name}
AMI: {ami_id}
State: {instance['State']['Name']}
Public IP: {instance.get('PublicIpAddress', 'N/A')}
Private IP: {instance.get('PrivateIpAddress', 'N/A')}

The instance is starting up. It may take a few minutes to be fully running."""
        
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
        
        # First, get instance details to show what we're terminating
        response = ec2.describe_instances(InstanceIds=[instance_id])
        
        if not response['Reservations'] or not response['Reservations'][0]['Instances']:
            return f"❌ Instance {instance_id} not found in {region}"
        
        instance = response['Reservations'][0]['Instances'][0]
        instance_name = "N/A"
        if 'Tags' in instance:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                    break
        
        current_state = instance['State']['Name']
        
        if current_state in ['terminated', 'shutting-down']:
            return f"❌ Instance {instance_id} ({instance_name}) is already {current_state}"
        
        # Terminate the instance
        terminate_response = ec2.terminate_instances(InstanceIds=[instance_id])
        
        terminated_instance = terminate_response['TerminatingInstances'][0]
        
        return f"""✅ Successfully initiated termination of EC2 instance:
Instance ID: {instance_id}
Name: {instance_name}
Region: {region}
Previous State: {terminated_instance['PreviousState']['Name']}
Current State: {terminated_instance['CurrentState']['Name']}

⚠️  Note: Termination is irreversible and cannot be undone.
The instance will be completely removed and you'll stop being charged for it."""
        
    except Exception as e:
        return f"❌ Error terminating EC2 instance: {str(e)}"


@tool
def stop_ec2_instance(region: str, instance_id: str) -> str:
    """Stop an EC2 instance (can be restarted later)"""
    try:
        ec2 = get_aws_client("ec2", region)
        
        # First, get instance details
        response = ec2.describe_instances(InstanceIds=[instance_id])
        
        if not response['Reservations'] or not response['Reservations'][0]['Instances']:
            return f"❌ Instance {instance_id} not found in {region}"
        
        instance = response['Reservations'][0]['Instances'][0]
        instance_name = "N/A"
        if 'Tags' in instance:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                    break
        
        current_state = instance['State']['Name']
        
        if current_state == 'stopped':
            return f"✅ Instance {instance_id} ({instance_name}) is already stopped"
        
        if current_state in ['terminated', 'shutting-down']:
            return f"❌ Cannot stop instance {instance_id} ({instance_name}) - it's {current_state}"
        
        # Stop the instance
        stop_response = ec2.stop_instances(InstanceIds=[instance_id])
        
        stopped_instance = stop_response['StoppingInstances'][0]
        
        return f"""✅ Successfully initiated stop of EC2 instance:
Instance ID: {instance_id}
Name: {instance_name}
Region: {region}
Previous State: {stopped_instance['PreviousState']['Name']}
Current State: {stopped_instance['CurrentState']['Name']}

💡 Note: Stopped instances can be restarted later. You'll only be charged for storage."""
        
    except Exception as e:
        return f"❌ Error stopping EC2 instance: {str(e)}"


@tool
def start_ec2_instance(region: str, instance_id: str) -> str:
    """Start a stopped EC2 instance"""
    try:
        ec2 = get_aws_client("ec2", region)
        
        # First, get instance details
        response = ec2.describe_instances(InstanceIds=[instance_id])
        
        if not response['Reservations'] or not response['Reservations'][0]['Instances']:
            return f"❌ Instance {instance_id} not found in {region}"
        
        instance = response['Reservations'][0]['Instances'][0]
        instance_name = "N/A"
        if 'Tags' in instance:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                    break
        
        current_state = instance['State']['Name']
        
        if current_state == 'running':
            return f"✅ Instance {instance_id} ({instance_name}) is already running"
        
        if current_state not in ['stopped']:
            return f"❌ Cannot start instance {instance_id} ({instance_name}) - current state is {current_state}"
        
        # Start the instance
        start_response = ec2.start_instances(InstanceIds=[instance_id])
        
        started_instance = start_response['StartingInstances'][0]
        
        return f"""✅ Successfully initiated start of EC2 instance:
Instance ID: {instance_id}
Name: {instance_name}
Region: {region}
Previous State: {started_instance['PreviousState']['Name']}
Current State: {started_instance['CurrentState']['Name']}

🔄 The instance is starting up. It may take a few minutes to be fully running."""
        
    except Exception as e:
        return f"❌ Error starting EC2 instance: {str(e)}"


@tool
def list_security_groups(region: str, vpc_id: Optional[str] = None) -> str:
    """List security groups in the specified region"""
    try:
        ec2 = get_aws_client("ec2", region)
        
        filters = []
        if vpc_id:
            filters.append({'Name': 'vpc-id', 'Values': [vpc_id]})
        
        response = ec2.describe_security_groups(Filters=filters)
        
        if not response['SecurityGroups']:
            return f"No security groups found in {region}" + (f" for VPC {vpc_id}" if vpc_id else "")
        
        result = f"📋 Security Groups in {region}:\n"
        for sg in response['SecurityGroups']:
            result += f"""
- Security Group ID: {sg['GroupId']}
  Name: {sg['GroupName']}
  Description: {sg['Description']}
  VPC ID: {sg.get('VpcId', 'default')}
  Inbound Rules: {len(sg.get('IpPermissions', []))}
  Outbound Rules: {len(sg.get('IpPermissionsEgress', []))}
"""
        
        return result
        
    except Exception as e:
        return f"❌ Error listing security groups: {str(e)}"


@tool
def create_security_group(
    region: str,
    group_name: str,
    description: str,
    vpc_id: Optional[str] = None
) -> str:
    """Create a new security group"""
    # Validate required parameters
    is_valid, error_msg = validate_security_group_creation_params(region, group_name, description)
    if not is_valid:
        return f"❌ {error_msg}. Please provide all required information before creating the security group."
    
    try:
        ec2 = get_aws_client("ec2", region)
        
        # Create security group
        response = ec2.create_security_group(
            GroupName=group_name,
            Description=description,
            VpcId=vpc_id
        )
        
        group_id = response['GroupId']
        
        return f"""✅ Security group created successfully!

Security Group Details:
- Group ID: {group_id}
- Name: {group_name}
- Description: {description}
- VPC ID: {vpc_id or 'default'}

You can now add inbound and outbound rules to this security group.
"""
        
    except Exception as e:
        return f"❌ Error creating security group: {str(e)}"


@tool
def add_inbound_rule(
    region: str,
    security_group_id: str,
    protocol: str,
    port: int,
    source_ip: str = "0.0.0.0/0",
    description: Optional[str] = None
) -> str:
    """Add an inbound rule to a security group"""
    # Validate required parameters
    is_valid, error_msg = validate_rule_addition_params(region, security_group_id, protocol, port, source_ip)
    if not is_valid:
        return f"❌ {error_msg}. Please provide all required information before adding the rule."
    
    try:
        ec2 = get_aws_client("ec2", region)
        
        # Prepare the rule
        rule = {
            'IpProtocol': protocol,
            'FromPort': port,
            'ToPort': port,
            'IpRanges': [{'CidrIp': source_ip}]
        }
        
        if description:
            rule['IpRanges'][0]['Description'] = description
        
        # Add the rule
        ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[rule]
        )
        
        return f"""✅ Inbound rule added successfully!

Rule Details:
- Security Group: {security_group_id}
- Protocol: {protocol}
- Port: {port}
- Source IP: {source_ip}
- Description: {description or 'N/A'}

The rule is now active and will allow traffic from the specified source.
"""
        
    except Exception as e:
        return f"❌ Error adding inbound rule: {str(e)}"


@tool
def add_outbound_rule(
    region: str,
    security_group_id: str,
    protocol: str,
    port: int,
    destination_ip: str = "0.0.0.0/0",
    description: Optional[str] = None
) -> str:
    """Add an outbound rule to a security group"""
    # Validate required parameters
    is_valid, error_msg = validate_rule_addition_params(region, security_group_id, protocol, port, destination_ip)
    if not is_valid:
        return f"❌ {error_msg}. Please provide all required information before adding the rule."
    
    try:
        ec2 = get_aws_client("ec2", region)
        
        # Prepare the rule
        rule = {
            'IpProtocol': protocol,
            'FromPort': port,
            'ToPort': port,
            'IpRanges': [{'CidrIp': destination_ip}]
        }
        
        if description:
            rule['IpRanges'][0]['Description'] = description
        
        # Add the rule
        ec2.authorize_security_group_egress(
            GroupId=security_group_id,
            IpPermissions=[rule]
        )
        
        return f"""✅ Outbound rule added successfully!

Rule Details:
- Security Group: {security_group_id}
- Protocol: {protocol}
- Port: {port}
- Destination IP: {destination_ip}
- Description: {description or 'N/A'}

The rule is now active and will allow traffic to the specified destination.
"""
        
    except Exception as e:
        return f"❌ Error adding outbound rule: {str(e)}"


@tool
def remove_inbound_rule(
    region: str,
    security_group_id: str,
    protocol: str,
    port: int,
    source_ip: str = "0.0.0.0/0"
) -> str:
    """Remove an inbound rule from a security group"""
    try:
        ec2 = get_aws_client("ec2", region)
        
        # Prepare the rule to remove
        rule = {
            'IpProtocol': protocol,
            'FromPort': port,
            'ToPort': port,
            'IpRanges': [{'CidrIp': source_ip}]
        }
        
        # Remove the rule
        ec2.revoke_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[rule]
        )
        
        return f"""✅ Inbound rule removed successfully!

Removed Rule:
- Security Group: {security_group_id}
- Protocol: {protocol}
- Port: {port}
- Source IP: {source_ip}

The rule has been removed and traffic from this source will no longer be allowed.
"""
        
    except Exception as e:
        return f"❌ Error removing inbound rule: {str(e)}"


@tool
def remove_outbound_rule(
    region: str,
    security_group_id: str,
    protocol: str,
    port: int,
    destination_ip: str = "0.0.0.0/0"
) -> str:
    """Remove an outbound rule from a security group"""
    try:
        ec2 = get_aws_client("ec2", region)
        
        # Prepare the rule to remove
        rule = {
            'IpProtocol': protocol,
            'FromPort': port,
            'ToPort': port,
            'IpRanges': [{'CidrIp': destination_ip}]
        }
        
        # Remove the rule
        ec2.revoke_security_group_egress(
            GroupId=security_group_id,
            IpPermissions=[rule]
        )
        
        return f"""✅ Outbound rule removed successfully!

Removed Rule:
- Security Group: {security_group_id}
- Protocol: {protocol}
- Port: {port}
- Destination IP: {destination_ip}

The rule has been removed and traffic to this destination will no longer be allowed.
"""
        
    except Exception as e:
        return f"❌ Error removing outbound rule: {str(e)}"


@tool
def get_security_group_details(region: str, security_group_id: str) -> str:
    """Get detailed information about a specific security group"""
    try:
        ec2 = get_aws_client("ec2", region)
        
        response = ec2.describe_security_groups(GroupIds=[security_group_id])
        sg = response['SecurityGroups'][0]
        
        result = f"""📋 Security Group Details:

Basic Information:
- Group ID: {sg['GroupId']}
- Name: {sg['GroupName']}
- Description: {sg['Description']}
- VPC ID: {sg.get('VpcId', 'default')}
- Owner ID: {sg['OwnerId']}

Inbound Rules ({len(sg.get('IpPermissions', []))}):"""
        
        for rule in sg.get('IpPermissions', []):
            protocol = rule.get('IpProtocol', 'all')
            from_port = rule.get('FromPort', 'N/A')
            to_port = rule.get('ToPort', 'N/A')
            
            result += f"\n  - Protocol: {protocol}, Ports: {from_port}-{to_port}"
            
            for ip_range in rule.get('IpRanges', []):
                cidr = ip_range.get('CidrIp', 'N/A')
                desc = ip_range.get('Description', '')
                result += f"\n    Source: {cidr} {desc}"
        
        result += f"\n\nOutbound Rules ({len(sg.get('IpPermissionsEgress', []))}):"
        
        for rule in sg.get('IpPermissionsEgress', []):
            protocol = rule.get('IpProtocol', 'all')
            from_port = rule.get('FromPort', 'N/A')
            to_port = rule.get('ToPort', 'N/A')
            
            result += f"\n  - Protocol: {protocol}, Ports: {from_port}-{to_port}"
            
            for ip_range in rule.get('IpRanges', []):
                cidr = ip_range.get('CidrIp', 'N/A')
                desc = ip_range.get('Description', '')
                result += f"\n    Destination: {cidr} {desc}"
        
        return result
        
    except Exception as e:
        return f"❌ Error getting security group details: {str(e)}"


@tool
def delete_security_group(region: str, security_group_id: str) -> str:
    """Delete a security group (only if not in use)"""
    try:
        ec2 = get_aws_client("ec2", region)
        
        # Delete the security group
        ec2.delete_security_group(GroupId=security_group_id)
        
        return f"""✅ Security group deleted successfully!

Security Group ID: {security_group_id}

Note: Security groups can only be deleted if they are not associated with any instances or other resources.
"""
        
    except Exception as e:
        return f"❌ Error deleting security group: {str(e)}"


@tool
def create_web_server_security_group(region: str, vpc_id: Optional[str] = None) -> str:
    """Create a pre-configured security group for web servers with common rules"""
    try:
        ec2 = get_aws_client("ec2", region)
        
        # Create security group
        group_name = f"web-server-sg-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        response = ec2.create_security_group(
            GroupName=group_name,
            Description="Security group for web servers with HTTP/HTTPS access",
            VpcId=vpc_id
        )
        
        group_id = response['GroupId']
        
        # Add common web server rules
        rules = [
            # SSH access
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH access'}]
            },
            # HTTP access
            {
                'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTP access'}]
            },
            # HTTPS access
            {
                'IpProtocol': 'tcp',
                'FromPort': 443,
                'ToPort': 443,
                'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTPS access'}]
            }
        ]
        
        # Add inbound rules
        ec2.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=rules
        )
        
        return f"""✅ Web server security group created successfully!

Security Group Details:
- Group ID: {group_id}
- Name: {group_name}
- Description: Security group for web servers with HTTP/HTTPS access
- VPC ID: {vpc_id or 'default'}

Pre-configured Rules:
- SSH (22): 0.0.0.0/0
- HTTP (80): 0.0.0.0/0
- HTTPS (443): 0.0.0.0/0

This security group is ready to use with web servers!
"""
        
    except Exception as e:
        return f"❌ Error creating web server security group: {str(e)}"


# Create the interactive Strands agent
interactive_agent = Agent(
    model=OpenAIModel(
        client_args={
            "api_key": "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",
        },
        model_id="gpt-4o",
        params={
            "max_tokens": 1000,
            "temperature": 0.7,
        }
    ),
    tools=[
        get_data_collection_status,
        get_available_regions,
        get_instance_type_info,
        get_latest_amazon_linux_ami,
        create_ec2_instance,
        list_ec2_instances,
        terminate_ec2_instance,
        stop_ec2_instance,
        start_ec2_instance,
        list_security_groups,
        create_security_group,
        add_inbound_rule,
        add_outbound_rule,
        remove_inbound_rule,
        remove_outbound_rule,
        get_security_group_details,
        delete_security_group,
        create_web_server_security_group
    ],
    system_prompt="""You are an interactive Infrastructure-as-Code assistant specialized in AWS EC2 instance and security group management. 
You help users create and manage EC2 instances and security groups through a conversational interface.

**CRITICAL: DATA COLLECTION PROTOCOL**
You MUST collect ALL required information before calling any tools. Do NOT call tools with incomplete data.

**Step-by-Step Process:**
1. **Identify User Intent**: Determine what the user wants to do (create instance, manage security group, etc.)
2. **Collect ALL Required Data**: Ask for every piece of information needed for the operation
3. **Validate Information**: Confirm all collected data is correct and complete
4. **Execute Tool**: Only call the tool when you have ALL required parameters
5. **Report Results**: Provide clear feedback on the operation outcome

**Required Information for Each Operation:**

**EC2 Instance Creation - REQUIRED:**
- Region (MUST specify)
- Instance Type (MUST specify)
- Instance Name (MUST specify)
- Key Pair (optional but recommended)
- Security Group IDs (optional - can create new ones)
- Subnet ID (optional)
- User Data (optional)

**Security Group Creation - REQUIRED:**
- Region (MUST specify)
- Group Name (MUST specify)
- Description (MUST specify)
- VPC ID (optional)

**Adding Security Group Rules - REQUIRED:**
- Region (MUST specify)
- Security Group ID (MUST specify)
- Protocol (MUST specify: tcp, udp, icmp, etc.)
- Port (MUST specify)
- Source/Destination IP (MUST specify)
- Description (optional but recommended)

**Data Collection Rules:**
- Ask ONE question at a time
- Wait for user response before asking the next question
- Do NOT assume any values - always ask the user
- If user provides incomplete information, ask for the missing pieces
- Confirm all collected information before proceeding
- Use tools like get_available_regions() to help users make informed choices
- Use get_data_collection_status() to check what information is still needed

**Example Conversation Flow:**
1. "I'd like to help you create an EC2 instance. First, which AWS region would you like to use?"
2. [Wait for region response]
3. "Great! What instance type would you like? (e.g., t2.micro, t3.small)"
4. [Wait for instance type response]
5. "What would you like to name this instance?"
6. [Wait for name response]
7. "Do you have a key pair for SSH access? If so, what's the name?"
8. [Wait for key pair response]
9. "Would you like to use an existing security group or create a new one?"
10. [Wait for security group response]
11. "Perfect! Let me create your EC2 instance with these settings: [summarize all collected data]"
12. [Now call the tool with complete information]

**Available Operations:**
**EC2 Instances:**
- **Create**: Launch new EC2 instances (collect ALL required data first)
- **List**: Show existing instances with details
- **Stop**: Stop running instances (can be restarted)
- **Start**: Start stopped instances
- **Terminate**: Permanently delete instances (irreversible)

**Security Groups:**
- **List**: Show existing security groups with details
- **Create**: Create new security groups (collect ALL required data first)
- **Add Rules**: Add inbound or outbound rules (collect ALL required data first)
- **Remove Rules**: Remove specific rules from security groups
- **View Details**: Get detailed information about a security group
- **Delete**: Delete security groups (only if not in use)
- **Quick Setup**: Create pre-configured security groups (e.g., web server)

**Conversation Style:**
- Be friendly and helpful
- Ask one question at a time and wait for responses
- Provide explanations and recommendations
- Use tools to get real-time AWS information when helpful
- Always explain what you're doing and why
- Warn users about irreversible actions like termination
- Suggest best practices for security group configurations

**Security Group Best Practices:**
- Use specific IP ranges instead of 0.0.0.0/0 when possible
- Add descriptive comments to rules
- Follow the principle of least privilege
- Regularly review and clean up unused rules
- Use separate security groups for different purposes

**REMEMBER: NEVER call tools with incomplete data. Always collect ALL required information first!**"""
)


def main():
    """Main interactive session"""
    print("🤖 Interactive Strands IaC Agent")
    print("=" * 50)
    print("I'll help you create an EC2 instance through conversation.")
    print("Ask me anything about AWS EC2 or type 'help' for guidance.")
    print("Type 'quit' to exit.\n")
    
    # Start with a greeting
    response = interactive_agent("Hello! I'd like to create an EC2 instance. Can you help me get started?")
    print(f"🤖 Agent: {response}\n")
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye! Thanks for using the Interactive IaC Agent!")
                break
            
            # Get response from the agent
            response = interactive_agent(user_input)
            print(f"🤖 Agent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Thanks for using the Interactive IaC Agent!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
