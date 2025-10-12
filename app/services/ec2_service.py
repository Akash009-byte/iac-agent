"""
EC2 Service for fetching and managing EC2 instances
"""

import boto3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError
import logging

from models.ec2_instance import EC2Instance, EC2InstanceUpdate
from core.mongodb import get_database

logger = logging.getLogger(__name__)


class EC2Service:
    """Service for managing EC2 instances"""
    
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.ec2_instances
    
    def get_aws_client(self, service_name: str, region: str = "us-west-2"):
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
    
    def get_available_regions(self) -> List[str]:
        """Get list of available AWS regions"""
        # Only fetch from specific regions for now
        return ["us-east-1","us-east-2", "us-west-1"]
    
    def fetch_instances_from_aws(self, region: str) -> List[Dict[str, Any]]:
        """
        Fetch EC2 instances from AWS for a specific region
        
        Args:
            region: AWS region to fetch instances from
            
        Returns:
            List of instance data dictionaries
        """
        try:
            ec2 = self.get_aws_client("ec2", region)
            response = ec2.describe_instances()
            
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    # Extract instance name from tags
                    instance_name = None
                    tags_dict = {}
                    if 'Tags' in instance:
                        for tag in instance['Tags']:
                            if tag['Key'] == 'Name':
                                instance_name = tag['Value']
                            tags_dict[tag['Key']] = tag['Value']
                    
                    # Extract security groups
                    security_groups = []
                    if 'SecurityGroups' in instance:
                        security_groups = [sg['GroupId'] for sg in instance['SecurityGroups']]
                    
                    # Calculate runtime
                    launch_time = instance['LaunchTime']
                    # Convert launch_time to UTC if it's timezone-aware, otherwise keep as-is
                    if launch_time.tzinfo is not None:
                        launch_time = launch_time.replace(tzinfo=None)
                    
                    current_time = datetime.utcnow()
                    runtime_seconds = (current_time - launch_time).total_seconds()
                    
                    instance_data = {
                        'instance_id': instance['InstanceId'],
                        'instance_type': instance['InstanceType'],
                        'region': region,
                        'state': instance['State']['Name'],
                        'public_ip': instance.get('PublicIpAddress'),
                        'private_ip': instance.get('PrivateIpAddress'),
                        'instance_name': instance_name,
                        'ami_id': instance.get('ImageId'),
                        'key_name': instance.get('KeyName'),
                        'launch_time': launch_time,
                        'runtime_seconds': runtime_seconds,
                        'tags': tags_dict if tags_dict else None,
                        'security_groups': security_groups if security_groups else None,
                        'vpc_id': instance.get('VpcId'),
                        'subnet_id': instance.get('SubnetId'),
                        'last_updated': current_time
                    }
                    
                    instances.append(instance_data)
            
            logger.info(f"Fetched {len(instances)} instances from region {region}")
            return instances
            
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise ValueError("AWS credentials not configured")
        except ClientError as e:
            logger.error(f"AWS API error: {e}")
            raise ValueError(f"AWS API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching instances: {e}")
            raise ValueError(f"Error fetching instances: {e}")
    
    def fetch_all_instances(self) -> List[Dict[str, Any]]:
        """
        Fetch EC2 instances from all available regions
        
        Returns:
            List of all instance data dictionaries
        """
        all_instances = []
        regions = self.get_available_regions()
        
        for region in regions:
            try:
                instances = self.fetch_instances_from_aws(region)
                all_instances.extend(instances)
            except Exception as e:
                logger.warning(f"Failed to fetch instances from region {region}: {e}")
                continue
        
        logger.info(f"Total instances fetched: {len(all_instances)}")
        return all_instances
    
    async def store_instance(self, instance_data: Dict[str, Any]) -> bool:
        """
        Store or update EC2 instance in MongoDB
        
        Args:
            instance_data: Instance data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            instance_id = instance_data['instance_id']
            
            # Check if instance already exists
            existing_instance = await self.collection.find_one({'instance_id': instance_id})
            
            if existing_instance:
                # Update existing instance
                update_data = EC2InstanceUpdate(**instance_data)
                result = await self.collection.update_one(
                    {'instance_id': instance_id},
                    {'$set': update_data.model_dump(exclude_none=True)}
                )
                logger.info(f"Updated instance {instance_id}")
                return result.modified_count > 0
            else:
                # Insert new instance
                instance = EC2Instance(**instance_data)
                result = await self.collection.insert_one(instance.to_dict())
                logger.info(f"Inserted new instance {instance_id}")
                return result.inserted_id is not None
                
        except Exception as e:
            logger.error(f"Error storing instance {instance_data.get('instance_id', 'unknown')}: {e}")
            return False
    
    async def store_all_instances(self, instances: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Store multiple instances in MongoDB
        
        Args:
            instances: List of instance data dictionaries
            
        Returns:
            Dictionary with counts of inserted and updated instances
        """
        inserted_count = 0
        updated_count = 0
        
        for instance_data in instances:
            try:
                instance_id = instance_data['instance_id']
                
                # Check if instance already exists
                existing_instance = await self.collection.find_one({'instance_id': instance_id})
                
                if existing_instance:
                    # Update existing instance
                    update_data = EC2InstanceUpdate(**instance_data)
                    result = await self.collection.update_one(
                        {'instance_id': instance_id},
                        {'$set': update_data.model_dump(exclude_none=True)}
                    )
                    if result.modified_count > 0:
                        updated_count += 1
                else:
                    # Insert new instance
                    instance = EC2Instance(**instance_data)
                    result = await self.collection.insert_one(instance.to_dict())
                    if result.inserted_id:
                        inserted_count += 1
                        
            except Exception as e:
                logger.error(f"Error storing instance {instance_data.get('instance_id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Stored instances - Inserted: {inserted_count}, Updated: {updated_count}")
        return {
            'inserted': inserted_count,
            'updated': updated_count,
            'total_processed': len(instances)
        }
    
    async def get_all_instances_from_db(self) -> List[Dict[str, Any]]:
        """
        Get all instances from MongoDB
        
        Returns:
            List of instance dictionaries
        """
        try:
            cursor = self.collection.find()
            instances = await cursor.to_list(length=None)
            # Convert ObjectId to string for JSON serialization
            for instance in instances:
                if '_id' in instance:
                    instance['_id'] = str(instance['_id'])
            return instances
        except Exception as e:
            logger.error(f"Error fetching instances from database: {e}")
            return []
    
    async def get_instance_by_id(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific instance by ID from MongoDB
        
        Args:
            instance_id: EC2 instance ID
            
        Returns:
            Instance dictionary or None if not found
        """
        try:
            instance = await self.collection.find_one({'instance_id': instance_id})
            if instance and '_id' in instance:
                instance['_id'] = str(instance['_id'])
            return instance
        except Exception as e:
            logger.error(f"Error fetching instance {instance_id}: {e}")
            return None
    
    async def delete_instance(self, instance_id: str) -> bool:
        """
        Delete instance from MongoDB
        
        Args:
            instance_id: EC2 instance ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            result = await self.collection.delete_one({'instance_id': instance_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting instance {instance_id}: {e}")
            return False
    
    async def sync_instances_from_aws(self) -> Dict[str, Any]:
        """
        Sync all instances from AWS and store in MongoDB
        
        Returns:
            Dictionary with sync results
        """
        try:
            # Fetch all instances from AWS
            instances = self.fetch_all_instances()
            
            if not instances:
                return {
                    'success': False,
                    'message': 'No instances found or failed to fetch from AWS',
                    'instances': []
                }
            
            # Store instances in MongoDB
            store_results = await self.store_all_instances(instances)
            
            return {
                'success': True,
                'message': f'Successfully synced {len(instances)} instances',
                'instances': instances,
                'store_results': store_results
            }
            
        except Exception as e:
            logger.error(f"Error syncing instances: {e}")
            return {
                'success': False,
                'message': f'Error syncing instances: {str(e)}',
                'instances': []
            }
