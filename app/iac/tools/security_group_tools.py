"""
Security Group management tools for the IaC Agent
"""

import os
import requests
from datetime import datetime
from typing import Optional
from strands import tool
from .validation import validate_security_group_creation_params, validate_rule_addition_params


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


@tool
def get_current_ip_address() -> str:
    """Get the current public IP address of the user"""
    try:
        # Try multiple IP services for reliability
        ip_services = [
            "https://api.ipify.org",
            "https://ipinfo.io/ip",
            "https://checkip.amazonaws.com",
            "https://icanhazip.com"
        ]
        
        for service in ip_services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    ip_address = response.text.strip()
                    if ip_address and len(ip_address.split('.')) == 4:
                        return f"""🌐 Your current public IP address: {ip_address}

💡 **Usage Tips:**
- Use this IP address in security group rules to allow access only from your current location
- For inbound rules: Source IP = {ip_address}/32
- For outbound rules: Destination IP = {ip_address}/32
- Note: Your IP may change if you're using a dynamic connection

🔒 **Security Best Practice:**
Using your specific IP address ({ip_address}/32) is more secure than using 0.0.0.0/0 (all IPs) as it restricts access to only your current location."""
            except Exception:
                continue
        
        return "❌ Unable to determine your current IP address. Please check your internet connection or specify an IP address manually."
        
    except Exception as e:
        return f"❌ Error getting IP address: {str(e)}"
