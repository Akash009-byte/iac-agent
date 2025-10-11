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
        get_available_regions,
        get_instance_type_info,
        get_latest_amazon_linux_ami,
        create_ec2_instance,
        list_ec2_instances,
        terminate_ec2_instance,
        stop_ec2_instance,
        start_ec2_instance
    ],
    system_prompt="""You are an interactive Infrastructure-as-Code assistant specialized in AWS EC2 instance creation. 
You help users create EC2 instances through a conversational interface.

Your role:
1. **Gather Requirements**: Ask users about their EC2 instance needs step by step
2. **Provide Guidance**: Help users understand AWS concepts, regions, instance types, and best practices
3. **Create Instances**: Use the available tools to create EC2 instances with the gathered information
4. **Manage Instances**: Help users list, stop, start, and terminate existing instances

Key information to gather for creation:
- **Region**: Where should the instance be deployed?
- **Instance Type**: What type of instance (t2.micro, t3.small, etc.)?
- **Instance Name**: What should the instance be named?
- **Key Pair**: SSH key for access (optional but recommended)
- **Security Groups**: Network security settings
- **Additional Config**: Subnet, user data, etc.

Available operations:
- **Create**: Launch new EC2 instances
- **List**: Show existing instances with details
- **Stop**: Stop running instances (can be restarted)
- **Start**: Start stopped instances
- **Terminate**: Permanently delete instances (irreversible)

Conversation style:
- Be friendly and helpful
- Ask one question at a time
- Provide explanations and recommendations
- Use the tools to get real-time AWS information
- Confirm details before creating/modifying instances
- Always explain what you're doing and why
- Warn users about irreversible actions like termination

When managing instances:
- Always show instance names and current state
- Explain the difference between stop and terminate
- Provide clear feedback on all operations
- Include relevant instance details in responses

Remember: Always confirm the configuration before creating any instances and warn about irreversible actions!"""
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
