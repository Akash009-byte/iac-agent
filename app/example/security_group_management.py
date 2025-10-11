#!/usr/bin/env python3
"""
Example: Security Group Management using boto3

This example demonstrates how to manage AWS Security Groups using boto3.
It includes creating, updating, and managing security group rules.
"""

import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional, List


class SecurityGroupManager:
    """Manages AWS Security Groups and their rules"""
    
    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize EC2 client
        
        Args:
            region_name: AWS region name
        """
        self.ec2_client = boto3.client('ec2', region_name=region_name)
        self.region_name = region_name
    
    def list_security_groups(self, vpc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List security groups in the region"""
        try:
            filters = []
            if vpc_id:
                filters.append({'Name': 'vpc-id', 'Values': [vpc_id]})
            
            response = self.ec2_client.describe_security_groups(Filters=filters)
            return response['SecurityGroups']
        except ClientError as e:
            print(f"Error listing security groups: {e}")
            return []
    
    def create_security_group(self, 
                             group_name: str, 
                             description: str, 
                             vpc_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new security group"""
        try:
            response = self.ec2_client.create_security_group(
                GroupName=group_name,
                Description=description,
                VpcId=vpc_id
            )
            
            return {
                'success': True,
                'group_id': response['GroupId'],
                'group_name': group_name,
                'description': description,
                'vpc_id': vpc_id
            }
        except ClientError as e:
            return {
                'success': False,
                'error': e.response['Error']['Message']
            }
    
    def add_inbound_rule(self, 
                        security_group_id: str,
                        protocol: str,
                        port: int,
                        source_ip: str = "0.0.0.0/0",
                        description: Optional[str] = None) -> Dict[str, Any]:
        """Add an inbound rule to a security group"""
        try:
            rule = {
                'IpProtocol': protocol,
                'FromPort': port,
                'ToPort': port,
                'IpRanges': [{'CidrIp': source_ip}]
            }
            
            if description:
                rule['IpRanges'][0]['Description'] = description
            
            self.ec2_client.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[rule]
            )
            
            return {
                'success': True,
                'message': f"Inbound rule added: {protocol}:{port} from {source_ip}"
            }
        except ClientError as e:
            return {
                'success': False,
                'error': e.response['Error']['Message']
            }
    
    def add_outbound_rule(self, 
                         security_group_id: str,
                         protocol: str,
                         port: int,
                         destination_ip: str = "0.0.0.0/0",
                         description: Optional[str] = None) -> Dict[str, Any]:
        """Add an outbound rule to a security group"""
        try:
            rule = {
                'IpProtocol': protocol,
                'FromPort': port,
                'ToPort': port,
                'IpRanges': [{'CidrIp': destination_ip}]
            }
            
            if description:
                rule['IpRanges'][0]['Description'] = description
            
            self.ec2_client.authorize_security_group_egress(
                GroupId=security_group_id,
                IpPermissions=[rule]
            )
            
            return {
                'success': True,
                'message': f"Outbound rule added: {protocol}:{port} to {destination_ip}"
            }
        except ClientError as e:
            return {
                'success': False,
                'error': e.response['Error']['Message']
            }
    
    def remove_inbound_rule(self, 
                           security_group_id: str,
                           protocol: str,
                           port: int,
                           source_ip: str = "0.0.0.0/0") -> Dict[str, Any]:
        """Remove an inbound rule from a security group"""
        try:
            rule = {
                'IpProtocol': protocol,
                'FromPort': port,
                'ToPort': port,
                'IpRanges': [{'CidrIp': source_ip}]
            }
            
            self.ec2_client.revoke_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[rule]
            )
            
            return {
                'success': True,
                'message': f"Inbound rule removed: {protocol}:{port} from {source_ip}"
            }
        except ClientError as e:
            return {
                'success': False,
                'error': e.response['Error']['Message']
            }
    
    def remove_outbound_rule(self, 
                            security_group_id: str,
                            protocol: str,
                            port: int,
                            destination_ip: str = "0.0.0.0/0") -> Dict[str, Any]:
        """Remove an outbound rule from a security group"""
        try:
            rule = {
                'IpProtocol': protocol,
                'FromPort': port,
                'ToPort': port,
                'IpRanges': [{'CidrIp': destination_ip}]
            }
            
            self.ec2_client.revoke_security_group_egress(
                GroupId=security_group_id,
                IpPermissions=[rule]
            )
            
            return {
                'success': True,
                'message': f"Outbound rule removed: {protocol}:{port} to {destination_ip}"
            }
        except ClientError as e:
            return {
                'success': False,
                'error': e.response['Error']['Message']
            }
    
    def get_security_group_details(self, security_group_id: str) -> Dict[str, Any]:
        """Get detailed information about a security group"""
        try:
            response = self.ec2_client.describe_security_groups(GroupIds=[security_group_id])
            return response['SecurityGroups'][0]
        except ClientError as e:
            return {'error': e.response['Error']['Message']}
    
    def delete_security_group(self, security_group_id: str) -> Dict[str, Any]:
        """Delete a security group"""
        try:
            self.ec2_client.delete_security_group(GroupId=security_group_id)
            return {
                'success': True,
                'message': f"Security group {security_group_id} deleted successfully"
            }
        except ClientError as e:
            return {
                'success': False,
                'error': e.response['Error']['Message']
            }
    
    def create_web_server_security_group(self, vpc_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a pre-configured security group for web servers"""
        try:
            from datetime import datetime
            group_name = f"web-server-sg-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            # Create security group
            response = self.ec2_client.create_security_group(
                GroupName=group_name,
                Description="Security group for web servers with HTTP/HTTPS access",
                VpcId=vpc_id
            )
            
            group_id = response['GroupId']
            
            # Add common web server rules
            rules = [
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH access'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTP access'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 443,
                    'ToPort': 443,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTPS access'}]
                }
            ]
            
            # Add inbound rules
            self.ec2_client.authorize_security_group_ingress(
                GroupId=group_id,
                IpPermissions=rules
            )
            
            return {
                'success': True,
                'group_id': group_id,
                'group_name': group_name,
                'message': 'Web server security group created with SSH, HTTP, and HTTPS access'
            }
        except ClientError as e:
            return {
                'success': False,
                'error': e.response['Error']['Message']
            }


def main():
    """Example usage of SecurityGroupManager"""
    
    # Initialize the manager
    sg_manager = SecurityGroupManager(region_name='us-east-1')
    
    print("🔒 Security Group Management Example")
    print("=" * 50)
    
    # Example 1: List existing security groups
    print("\n=== Example 1: List Security Groups ===")
    security_groups = sg_manager.list_security_groups()
    print(f"Found {len(security_groups)} security groups:")
    for sg in security_groups[:3]:  # Show first 3
        print(f"  - {sg['GroupId']}: {sg['GroupName']} ({sg['Description']})")
    
    # Example 2: Create a new security group
    print("\n=== Example 2: Create Security Group ===")
    result = sg_manager.create_security_group(
        group_name="example-security-group",
        description="Example security group for testing",
        vpc_id=None  # Use default VPC
    )
    
    if result['success']:
        group_id = result['group_id']
        print(f"✅ Security group created: {group_id}")
        
        # Example 3: Add inbound rules
        print("\n=== Example 3: Add Inbound Rules ===")
        inbound_rules = [
            ('tcp', 22, '0.0.0.0/0', 'SSH access'),
            ('tcp', 80, '0.0.0.0/0', 'HTTP access'),
            ('tcp', 443, '0.0.0.0/0', 'HTTPS access')
        ]
        
        for protocol, port, source_ip, description in inbound_rules:
            result = sg_manager.add_inbound_rule(
                security_group_id=group_id,
                protocol=protocol,
                port=port,
                source_ip=source_ip,
                description=description
            )
            if result['success']:
                print(f"✅ {result['message']}")
            else:
                print(f"❌ Error: {result['error']}")
        
        # Example 4: Add outbound rules
        print("\n=== Example 4: Add Outbound Rules ===")
        outbound_rules = [
            ('tcp', 80, '0.0.0.0/0', 'HTTP outbound'),
            ('tcp', 443, '0.0.0.0/0', 'HTTPS outbound'),
            ('tcp', 53, '0.0.0.0/0', 'DNS outbound')
        ]
        
        for protocol, port, destination_ip, description in outbound_rules:
            result = sg_manager.add_outbound_rule(
                security_group_id=group_id,
                protocol=protocol,
                port=port,
                destination_ip=destination_ip,
                description=description
            )
            if result['success']:
                print(f"✅ {result['message']}")
            else:
                print(f"❌ Error: {result['error']}")
        
        # Example 5: Get security group details
        print("\n=== Example 5: Security Group Details ===")
        details = sg_manager.get_security_group_details(group_id)
        if 'error' not in details:
            print(f"Group ID: {details['GroupId']}")
            print(f"Name: {details['GroupName']}")
            print(f"Description: {details['Description']}")
            print(f"Inbound Rules: {len(details.get('IpPermissions', []))}")
            print(f"Outbound Rules: {len(details.get('IpPermissionsEgress', []))}")
        
        # Example 6: Remove a rule
        print("\n=== Example 6: Remove Rule ===")
        result = sg_manager.remove_inbound_rule(
            security_group_id=group_id,
            protocol='tcp',
            port=22,
            source_ip='0.0.0.0/0'
        )
        if result['success']:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ Error: {result['error']}")
        
        # Example 7: Delete security group
        print("\n=== Example 7: Delete Security Group ===")
        result = sg_manager.delete_security_group(group_id)
        if result['success']:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    else:
        print(f"❌ Error creating security group: {result['error']}")
    
    # Example 8: Create web server security group
    print("\n=== Example 8: Web Server Security Group ===")
    result = sg_manager.create_web_server_security_group()
    if result['success']:
        print(f"✅ {result['message']}")
        print(f"Group ID: {result['group_id']}")
        print(f"Group Name: {result['group_name']}")
        
        # Clean up
        sg_manager.delete_security_group(result['group_id'])
        print("🧹 Cleaned up web server security group")
    else:
        print(f"❌ Error: {result['error']}")


if __name__ == "__main__":
    main()
