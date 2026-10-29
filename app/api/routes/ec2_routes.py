"""
EC2 API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
import logging

from services.ec2_service import EC2Service
from models.ec2_instance import EC2Instance

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ec2", tags=["EC2 Instances"])


def get_ec2_service() -> EC2Service:
    """Dependency to get EC2 service instance"""
    return EC2Service()


@router.get("/instances", response_model=List[Dict[str, Any]])
async def get_instances(
    ec2_service: EC2Service = Depends(get_ec2_service),
    sync: bool = Query(False, description="Sync from AWS before returning results")
):
    """
    Get all EC2 instances

    Args:
        sync: If True, sync from AWS before returning results

    Returns:
        List of EC2 instances
    """
    try:
        if sync:
            # Sync from AWS and return updated data
            sync_result = await ec2_service.sync_instances_from_aws()
            if not sync_result['success']:
                raise HTTPException(status_code=500, detail=sync_result['message'])
            return sync_result['instances']
        else:
            # Return cached data from MongoDB
            instances = await ec2_service.get_all_instances_from_db()
            return instances

    except Exception as e:
        logger.error(f"Error getting instances: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting instances: {str(e)}")


@router.get("/instances/{instance_id}", response_model=Dict[str, Any])
async def get_instance(
    instance_id: str,
    ec2_service: EC2Service = Depends(get_ec2_service)
):
    """
    Get specific EC2 instance by ID

    Args:
        instance_id: EC2 instance ID

    Returns:
        EC2 instance data
    """
    try:
        instance = await ec2_service.get_instance_by_id(instance_id)
        if not instance:
            raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
        return instance

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting instance {instance_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting instance: {str(e)}")


@router.post("/instances/sync")
async def sync_instances(
    ec2_service: EC2Service = Depends(get_ec2_service)
):
    """
    Sync EC2 instances from AWS and store in MongoDB

    Returns:
        Sync results
    """
    try:
        result = await ec2_service.sync_instances_from_aws()

        if not result['success']:
            raise HTTPException(status_code=500, detail=result['message'])

        return {
            "success": True,
            "message": result['message'],
            "instances_count": len(result['instances']),
            "store_results": result['store_results']
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing instances: {e}")
        raise HTTPException(status_code=500, detail=f"Error syncing instances: {str(e)}")


@router.get("/instances/region/{region}", response_model=List[Dict[str, Any]])
async def get_instances_by_region(
    region: str,
    ec2_service: EC2Service = Depends(get_ec2_service),
    sync: bool = Query(False, description="Sync from AWS before returning results")
):
    """
    Get EC2 instances for a specific region

    Args:
        region: AWS region
        sync: If True, sync from AWS before returning results

    Returns:
        List of EC2 instances for the region
    """
    try:
        if sync:
            # Fetch from AWS for specific region
            instances = ec2_service.fetch_instances_from_aws(region)
            # Store in MongoDB
            await ec2_service.store_all_instances(instances)
            return instances
        else:
            # Return cached data from MongoDB for the region
            instances = await ec2_service.get_all_instances_from_db()
            region_instances = [inst for inst in instances if inst.get('region') == region]
            return region_instances

    except Exception as e:
        logger.error(f"Error getting instances for region {region}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting instances: {str(e)}")


@router.delete("/instances/{instance_id}")
async def delete_instance(
    instance_id: str,
    ec2_service: EC2Service = Depends(get_ec2_service)
):
    """
    Delete EC2 instance from MongoDB

    Args:
        instance_id: EC2 instance ID

    Returns:
        Deletion result
    """
    try:
        success = await ec2_service.delete_instance(instance_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")

        return {
            "success": True,
            "message": f"Instance {instance_id} deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting instance {instance_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting instance: {str(e)}")


@router.get("/regions", response_model=List[str])
async def get_available_regions(
    ec2_service: EC2Service = Depends(get_ec2_service)
):
    """
    Get list of available AWS regions

    Returns:
        List of AWS region names
    """
    try:
        regions = ec2_service.get_available_regions()
        return regions

    except Exception as e:
        logger.error(f"Error getting regions: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting regions: {str(e)}")


@router.get("/instances/stats")
async def get_instance_stats(
    ec2_service: EC2Service = Depends(get_ec2_service)
):
    """
    Get EC2 instance statistics

    Returns:
        Instance statistics
    """
    try:
        instances = await ec2_service.get_all_instances_from_db()

        # Calculate statistics
        total_instances = len(instances)
        running_instances = len([inst for inst in instances if inst.get('state') == 'running'])
        stopped_instances = len([inst for inst in instances if inst.get('state') == 'stopped'])
        pending_instances = len([inst for inst in instances if inst.get('state') == 'pending'])

        # Group by region
        regions = {}
        for instance in instances:
            region = instance.get('region', 'unknown')
            if region not in regions:
                regions[region] = 0
            regions[region] += 1

        # Group by instance type
        instance_types = {}
        for instance in instances:
            instance_type = instance.get('instance_type', 'unknown')
            if instance_type not in instance_types:
                instance_types[instance_type] = 0
            instance_types[instance_type] += 1

        return {
            "total_instances": total_instances,
            "running_instances": running_instances,
            "stopped_instances": stopped_instances,
            "pending_instances": pending_instances,
            "regions": regions,
            "instance_types": instance_types
        }

    except Exception as e:
        logger.error(f"Error getting instance stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")
