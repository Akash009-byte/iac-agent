"""
Infrastructure-as-Code (IaC) Automation Agent

This agent provides natural language interface for AWS infrastructure management
using the Strands SDK. It can create, manage, and destroy AWS resources like
EC2 instances, VPCs, security groups, and more.
"""

from strands import Agent, tool
from strands.models.openai import OpenAIModel
import boto3
from typing import Optional, Dict, Any, List
import json
import os


def get_aws_client(service_name: str, region: str):
    """
    Create AWS client with credentials from environment variables.
    
    Args:
        service_name: AWS service name (e.g., 'ec2', 's3')
        region: AWS region
    
    Returns:
        AWS client instance
    """
    # Get credentials from environment variables
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_session_token = os.getenv('AWS_SESSION_TOKEN')
    aws_default_region = os.getenv('AWS_DEFAULT_REGION', region)
    
    # Validate that required credentials are present
    if not aws_access_key_id or not aws_secret_access_key:
        raise ValueError("AWS credentials not found in environment variables. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.")
    
    # Create session with credentials
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        region_name=aws_default_region
    )
    
    return session.client(service_name, region_name=region)


@tool
def create_ec2_instance(
    region: str, 
    instance_type: str = "t2.micro", 
    ami: str = "ami-0c55b159cbfafe1f0",
    key_name: Optional[str] = None,
    security_group_ids: Optional[List[str]] = None,
    subnet_id: Optional[str] = None,
    user_data: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None
) -> str:
    """
    Launch an EC2 instance in the given region using AWS SDK.
    
    Args:
        region: AWS region (e.g., 'us-west-2', 'us-east-1')
        instance_type: EC2 instance type (default: 't2.micro')
        ami: Amazon Machine Image ID (default: Amazon Linux 2)
        key_name: SSH key pair name for instance access
        security_group_ids: List of security group IDs
        subnet_id: Subnet ID for the instance
        user_data: User data script to run on instance startup
        tags: Dictionary of tags to apply to the instance
    
    Returns:
        String with instance details and status
    """
    try:
        ec2 = get_aws_client("ec2", region)
        
        # Prepare launch parameters
        launch_params = {
            "ImageId": ami,
            "InstanceType": instance_type,
            "MinCount": 1,
            "MaxCount": 1
        }
        
        # Add optional parameters
        if key_name:
            launch_params["KeyName"] = key_name
        if security_group_ids:
            launch_params["SecurityGroupIds"] = security_group_ids
        if subnet_id:
            launch_params["SubnetId"] = subnet_id
        if user_data:
            launch_params["UserData"] = user_data
        
        # Launch the instance
        response = ec2.run_instances(**launch_params)
        instance_id = response["Instances"][0]["InstanceId"]
        
        # Add tags if provided
        if tags:
            ec2.create_tags(
                Resources=[instance_id],
                Tags=[{"Key": k, "Value": v} for k, v in tags.items()]
            )
        
        # Get instance details
        instance_details = ec2.describe_instances(InstanceIds=[instance_id])
        instance = instance_details["Reservations"][0]["Instances"][0]
        
        return f"""✅ Successfully created EC2 instance:
- Instance ID: {instance_id}
- Region: {region}
- Instance Type: {instance_type}
- AMI: {ami}
- State: {instance['State']['Name']}
- Public IP: {instance.get('PublicIpAddress', 'N/A')}
- Private IP: {instance.get('PrivateIpAddress', 'N/A')}"""
        
    except Exception as e:
        return f"❌ Error creating EC2 instance: {str(e)}"


@tool
def list_ec2_instances(region: str, state: Optional[str] = None) -> str:
    """
    List EC2 instances in the specified region.
    
    Args:
        region: AWS region to query
        state: Filter by instance state (running, stopped, pending, etc.)
    
    Returns:
        String with list of instances and their details
    """
    try:
        ec2 = get_aws_client("ec2", region)
        
        # Prepare filters
        filters = []
        if state:
            filters.append({"Name": "instance-state-name", "Values": [state]})
        
        response = ec2.describe_instances(Filters=filters)
        
        instances = []
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                instances.append({
                    "InstanceId": instance["InstanceId"],
                    "InstanceType": instance["InstanceType"],
                    "State": instance["State"]["Name"],
                    "PublicIp": instance.get("PublicIpAddress", "N/A"),
                    "PrivateIp": instance.get("PrivateIpAddress", "N/A"),
                    "LaunchTime": instance["LaunchTime"].strftime("%Y-%m-%d %H:%M:%S")
                })
        
        if not instances:
            return f"No EC2 instances found in {region}" + (f" with state '{state}'" if state else "")
        
        result = f"📋 EC2 Instances in {region}:\n"
        for instance in instances:
            result += f"""
- Instance ID: {instance['InstanceId']}
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
    """
    Terminate an EC2 instance.
    
    Args:
        region: AWS region where the instance is located
        instance_id: ID of the instance to terminate
    
    Returns:
        String with termination status
    """
    try:
        ec2 = get_aws_client("ec2", region)
        
        response = ec2.terminate_instances(InstanceIds=[instance_id])
        
        instance = response["TerminatingInstances"][0]
        return f"""✅ Successfully initiated termination of EC2 instance:
- Instance ID: {instance_id}
- Current State: {instance['CurrentState']['Name']}
- Previous State: {instance['PreviousState']['Name']}"""
        
    except Exception as e:
        return f"❌ Error terminating EC2 instance: {str(e)}"


@tool
def create_security_group(
    region: str,
    group_name: str,
    description: str,
    vpc_id: Optional[str] = None
) -> str:
    """
    Create a security group in the specified region.
    
    Args:
        region: AWS region
        group_name: Name for the security group
        description: Description of the security group
        vpc_id: VPC ID (uses default VPC if not specified)
    
    Returns:
        String with security group details
    """
    try:
        ec2 = get_aws_client("ec2", region)
        
        # Get default VPC if not specified
        if not vpc_id:
            vpcs = ec2.describe_vpcs(Filters=[{"Name": "is-default", "Values": ["true"]}])
            if vpcs["Vpcs"]:
                vpc_id = vpcs["Vpcs"][0]["VpcId"]
            else:
                return "❌ No default VPC found. Please specify a VPC ID."
        
        response = ec2.create_security_group(
            GroupName=group_name,
            Description=description,
            VpcId=vpc_id
        )
        
        group_id = response["GroupId"]
        
        return f"""✅ Successfully created security group:
- Group ID: {group_id}
- Group Name: {group_name}
- Description: {description}
- VPC ID: {vpc_id}"""
        
    except Exception as e:
        return f"❌ Error creating security group: {str(e)}"


@tool
def get_amazon_linux_ami(region: str) -> str:
    """
    Get the latest Amazon Linux 2 AMI ID for the specified region.
    
    Args:
        region: AWS region
    
    Returns:
        String with AMI ID and details
    """
    try:
        ec2 = get_aws_client("ec2", region)
        
        response = ec2.describe_images(
            Owners=["amazon"],
            Filters=[
                {"Name": "name", "Values": ["amzn2-ami-hvm-*"]},
                {"Name": "architecture", "Values": ["x86_64"]},
                {"Name": "state", "Values": ["available"]}
            ]
        )
        
        # Sort by creation date to get the latest
        images = sorted(response["Images"], key=lambda x: x["CreationDate"], reverse=True)
        
        if images:
            latest_ami = images[0]
            return f"""✅ Latest Amazon Linux 2 AMI:
- AMI ID: {latest_ami['ImageId']}
- Name: {latest_ami['Name']}
- Description: {latest_ami['Description']}
- Architecture: {latest_ami['Architecture']}
- Creation Date: {latest_ami['CreationDate']}"""
        else:
            return f"❌ No Amazon Linux 2 AMI found in {region}"
            
    except Exception as e:
        return f"❌ Error getting Amazon Linux AMI: {str(e)}"


# Create OpenAI model
openai_model  = OpenAIModel(
    client_args={
        "api_key": "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",
    },
    model_id="gpt-4o",
    params={
        "max_tokens": 1000,
        "temperature": 0.7,
    }
)

# Create the IaC agent with all tools using OpenAI
iac_agent = Agent(
    model=openai_model,
    tools=[
        create_ec2_instance,
        list_ec2_instances,
        terminate_ec2_instance,
        create_security_group,
        get_amazon_linux_ami
    ],
    system_prompt="""You are an Infrastructure-as-Code automation agent specialized in AWS infrastructure management. 
You can help users create, manage, and destroy AWS resources using natural language commands.

Your capabilities include:
- Creating EC2 instances with custom configurations
- Listing and managing existing EC2 instances
- Creating security groups
- Getting the latest Amazon Linux AMI IDs
- Terminating instances when needed

AWS Credentials:
The agent uses AWS credentials from environment variables:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_SESSION_TOKEN (optional, for temporary credentials)
- AWS_DEFAULT_REGION (optional, defaults to us-west-2)

Always provide clear, detailed responses about the actions you're taking and the results.
Be helpful in suggesting best practices for AWS infrastructure management.
If credentials are not properly configured, suggest setting the environment variables."""
)


def main():
    """Example usage of the IaC agent"""
    print("🚀 Infrastructure-as-Code Automation Agent")
    print("=" * 50)
    
    # Example 1: Get Amazon Linux AMI
    print("\n1. Getting latest Amazon Linux AMI for us-west-2:")
    response = iac_agent("Get the latest Amazon Linux 2 AMI for us-west-2 region")
    print(response)
    
    # # Example 2: Create EC2 instance
    # print("\n2. Creating EC2 instance:")
    # response = iac_agent("Spin up an EC2 instance in us-west-2 using Amazon Linux with t2.micro instance type")
    # print(response)
    
    # Example 3: List instances
    print("\n3. Listing running instances:")
    response = iac_agent("Show me all running EC2 instances in us-west-2")
    print(response)


if __name__ == "__main__":
    main()
