#!/usr/bin/env python3
"""
Activity Log Model for EC2Forge
Stores structured logs from Strands SDK operations
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from core.mongodb import PyObjectId


class ActivityLog(BaseModel):
    """Activity Log Entry Model"""

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    timestamp: datetime = Field(default_factory=datetime.now)
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    log_level: str = Field(..., description="DEBUG, WARNING, ERROR")
    tool_name: str = Field(..., description="Tool/operation name (e.g., ec2_create, ec2_terminate)")
    operation_type: str = Field(..., description="Type of operation (instance_creation, instance_termination, etc.)")
    session_id: Optional[str] = Field(None, description="User session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    message: str = Field(..., description="Log message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    execution_time_ms: Optional[int] = Field(None, description="Operation duration in milliseconds")
    status: str = Field(default="in_progress", description="success, failure, in_progress")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Tool-specific metadata")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ActivityLogFilter(BaseModel):
    """Filter model for activity logs"""

    start_date: Optional[str] = None
    end_date: Optional[str] = None
    log_levels: Optional[list[str]] = None
    tool_names: Optional[list[str]] = None
    operation_types: Optional[list[str]] = None
    status: Optional[list[str]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    search_text: Optional[str] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)


class ActivityLogStats(BaseModel):
    """Statistics for activity logs"""

    total_logs: int
    logs_by_level: Dict[str, int]
    logs_by_tool: Dict[str, int]
    logs_by_operation: Dict[str, int]
    logs_by_status: Dict[str, int]
    logs_by_date: Dict[str, int]
    average_execution_time: Optional[float] = None
    success_rate: float
