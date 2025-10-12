#!/usr/bin/env python3
"""
Activity Log API Routes
Provides endpoints for retrieving and filtering activity logs
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from core.mongodb import get_database
from models.activity_log import ActivityLog, ActivityLogFilter, ActivityLogStats
from core.log_config import logger

router = APIRouter(prefix="/activity-logs", tags=["Activity Logs"])


@router.get("/", response_model=List[ActivityLog])
async def get_activity_logs(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    log_levels: Optional[str] = Query(None, description="Comma-separated log levels"),
    tool_names: Optional[str] = Query(None, description="Comma-separated tool names"),
    operation_types: Optional[str] = Query(None, description="Comma-separated operation types"),
    status: Optional[str] = Query(None, description="Comma-separated statuses"),
    user_id: Optional[str] = Query(None, description="User ID filter"),
    session_id: Optional[str] = Query(None, description="Session ID filter"),
    search_text: Optional[str] = Query(None, description="Search in messages"),
    limit: int = Query(100, le=1000, description="Maximum number of logs to return"),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    sort_by: str = Query("timestamp", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)")
):
    """Get activity logs with filtering and pagination"""
    
    try:
        database = get_database()
        if database is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        collection = database["activity_logs"]
        
        # Build filter query
        query = {}
        
        # Date range filter
        if start_date or end_date:
            date_filter = {}
            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                    date_filter["$gte"] = start_dt
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid start_date format")
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                    date_filter["$lt"] = end_dt
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid end_date format")
            query["timestamp"] = date_filter
        
        # Array filters
        if log_levels:
            query["log_level"] = {"$in": [level.strip() for level in log_levels.split(",")]}
        
        if tool_names:
            query["tool_name"] = {"$in": [name.strip() for name in tool_names.split(",")]}
        
        if operation_types:
            query["operation_type"] = {"$in": [op.strip() for op in operation_types.split(",")]}
        
        if status:
            query["status"] = {"$in": [s.strip() for s in status.split(",")]}
        
        # Exact match filters
        if user_id:
            query["user_id"] = user_id
        
        if session_id:
            query["session_id"] = session_id
        
        # Text search
        if search_text:
            query["message"] = {"$regex": search_text, "$options": "i"}
        
        # Build sort criteria
        sort_criteria = [(sort_by, -1 if sort_order == "desc" else 1)]
        
        # Execute query
        cursor = collection.find(query).sort(sort_criteria).skip(offset).limit(limit)
        logs = await cursor.to_list(length=limit)
        
        # Convert to ActivityLog objects
        activity_logs = [ActivityLog(**log) for log in logs]
        
        return activity_logs
        
    except Exception as e:
        logger.error(f"Error retrieving activity logs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats", response_model=ActivityLogStats)
async def get_activity_log_stats(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    user_id: Optional[str] = Query(None, description="User ID filter")
):
    """Get statistics for activity logs"""
    
    try:
        database = get_database()
        if database is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        collection = database["activity_logs"]
        
        # Build base filter
        base_filter = {}
        if start_date or end_date:
            date_filter = {}
            if start_date:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                date_filter["$gte"] = start_dt
            if end_date:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                date_filter["$lt"] = end_dt
            base_filter["timestamp"] = date_filter
        
        if user_id:
            base_filter["user_id"] = user_id
        
        # Get total count
        total_logs = await collection.count_documents(base_filter)
        
        # Get counts by level
        level_pipeline = [
            {"$match": base_filter},
            {"$group": {"_id": "$log_level", "count": {"$sum": 1}}}
        ]
        level_cursor = collection.aggregate(level_pipeline)
        logs_by_level = {doc["_id"]: doc["count"] for doc in await level_cursor.to_list(length=None)}
        
        # Get counts by tool
        tool_pipeline = [
            {"$match": base_filter},
            {"$group": {"_id": "$tool_name", "count": {"$sum": 1}}}
        ]
        tool_cursor = collection.aggregate(tool_pipeline)
        logs_by_tool = {doc["_id"]: doc["count"] for doc in await tool_cursor.to_list(length=None)}
        
        # Get counts by operation
        operation_pipeline = [
            {"$match": base_filter},
            {"$group": {"_id": "$operation_type", "count": {"$sum": 1}}}
        ]
        operation_cursor = collection.aggregate(operation_pipeline)
        logs_by_operation = {doc["_id"]: doc["count"] for doc in await operation_cursor.to_list(length=None)}
        
        # Get counts by status
        status_pipeline = [
            {"$match": base_filter},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        status_cursor = collection.aggregate(status_pipeline)
        logs_by_status = {doc["_id"]: doc["count"] for doc in await status_cursor.to_list(length=None)}
        
        # Get counts by date
        date_pipeline = [
            {"$match": base_filter},
            {"$group": {"_id": "$date", "count": {"$sum": 1}}},
            {"$sort": {"_id": -1}},
            {"$limit": 30}  # Last 30 days
        ]
        date_cursor = collection.aggregate(date_pipeline)
        logs_by_date = {doc["_id"]: doc["count"] for doc in await date_cursor.to_list(length=None)}
        
        # Calculate average execution time
        execution_time_pipeline = [
            {"$match": {**base_filter, "execution_time_ms": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": None, "avg_time": {"$avg": "$execution_time_ms"}}}
        ]
        exec_time_cursor = collection.aggregate(execution_time_pipeline)
        exec_time_result = await exec_time_cursor.to_list(length=1)
        average_execution_time = exec_time_result[0]["avg_time"] if exec_time_result else None
        
        # Calculate success rate
        success_count = logs_by_status.get("success", 0)
        total_with_status = sum(logs_by_status.values())
        success_rate = (success_count / total_with_status * 100) if total_with_status > 0 else 0
        
        return ActivityLogStats(
            total_logs=total_logs,
            logs_by_level=logs_by_level,
            logs_by_tool=logs_by_tool,
            logs_by_operation=logs_by_operation,
            logs_by_status=logs_by_status,
            logs_by_date=logs_by_date,
            average_execution_time=average_execution_time,
            success_rate=success_rate
        )
        
    except Exception as e:
        logger.error(f"Error retrieving activity log stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/export")
async def export_activity_logs(
    format: str = Query("json", description="Export format (json/csv)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    log_levels: Optional[str] = Query(None, description="Comma-separated log levels"),
    tool_names: Optional[str] = Query(None, description="Comma-separated tool names")
):
    """Export activity logs in specified format"""
    
    try:
        database = get_database()
        if database is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        collection = database["activity_logs"]
        
        # Build filter (similar to get_activity_logs)
        query = {}
        print(f"================Logging the logs=============>")
        if start_date or end_date:
            date_filter = {}
            if start_date:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                date_filter["$gte"] = start_dt
            if end_date:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                date_filter["$lt"] = end_dt
            query["timestamp"] = date_filter
        
        if log_levels:
            query["log_level"] = {"$in": [level.strip() for level in log_levels.split(",")]}
        
        if tool_names:
            query["tool_name"] = {"$in": [name.strip() for name in tool_names.split(",")]}
        
        # Get all matching logs
        cursor = collection.find(query).sort([("timestamp", -1)])
        logs = await cursor.to_list(length=None)
        
        if format.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            if logs:
                fieldnames = logs[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(logs)
            
            return {
                "content": output.getvalue(),
                "filename": f"activity_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "content_type": "text/csv"
            }
        else:  # JSON format
            return {
                "content": logs,
                "filename": f"activity_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "content_type": "application/json"
            }
        
    except Exception as e:
        logger.error(f"Error exporting activity logs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/")
async def clear_activity_logs(
    days_to_keep: int = Query(30, ge=1, le=365, description="Number of days to keep")
):
    """Clear old activity logs (keep only recent ones)"""
    
    try:
        database = get_database()
        if database is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        collection = database["activity_logs"]
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Delete old logs
        result = await collection.delete_many({"timestamp": {"$lt": cutoff_date}})
        
        return {
            "message": f"Deleted {result.deleted_count} old activity logs",
            "deleted_count": result.deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error clearing activity logs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
