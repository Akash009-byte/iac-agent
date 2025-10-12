#!/usr/bin/env python3
"""
Tool Logger for EC2Forge
Wraps individual tools to add activity logging
"""

import time
import uuid
from datetime import datetime
from functools import wraps
from typing import Callable, Any, Dict, Optional
from core.activity_logger import activity_logger


def log_tool_usage(tool_name: str, operation_type: str = None):
    """
    Decorator to log tool usage for activity tracking
    
    Args:
        tool_name: Name of the tool being called
        operation_type: Type of operation (defaults to tool_name)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not operation_type:
                op_type = tool_name
            else:
                op_type = operation_type
            
            session_id = kwargs.get('session_id', f"session_{uuid.uuid4().hex[:8]}")
            user_id = kwargs.get('user_id', "demo_user")
            
            start_time = time.time()
            
            # Log tool start
            activity_logger.log_operation_start(
                tool_name=tool_name,
                operation_type=op_type,
                message=f"Starting {tool_name} operation",
                session_id=session_id,
                user_id=user_id,
                details={
                    "function": func.__name__,
                    "args": str(args)[:200] if args else "None",
                    "kwargs": str(kwargs)[:200] if kwargs else "None",
                    "started_at": datetime.now().isoformat()
                },
                metadata={
                    "tool_name": tool_name,
                    "operation_type": op_type
                }
            )
            
            try:
                # Execute the original function
                result = func(*args, **kwargs)
                
                # Log successful completion
                execution_time = int((time.time() - start_time) * 1000)
                activity_logger.log_operation_complete(
                    tool_name=tool_name,
                    operation_type=op_type,
                    message=f"Successfully completed {tool_name} operation",
                    session_id=session_id,
                    user_id=user_id,
                    execution_time_ms=execution_time,
                    status="success",
                    details={
                        "result_type": type(result).__name__,
                        "completed_at": datetime.now().isoformat()
                    },
                    metadata={
                        "result_preview": str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
                    }
                )
                
                return result
                
            except Exception as e:
                # Log error
                execution_time = int((time.time() - start_time) * 1000)
                activity_logger.log_operation_complete(
                    tool_name=tool_name,
                    operation_type=op_type,
                    message=f"Failed to execute {tool_name} operation: {str(e)}",
                    session_id=session_id,
                    user_id=user_id,
                    execution_time_ms=execution_time,
                    status="failure",
                    details={
                        "error": str(e),
                        "failed_at": datetime.now().isoformat()
                    },
                    metadata={
                        "error_type": type(e).__name__
                    }
                )
                
                # Re-raise the exception
                raise e
                
        return wrapper
    return decorator


def create_logged_tool(original_func: Callable, tool_name: str, operation_type: str = None) -> Callable:
    """
    Create a logged version of a tool function
    
    Args:
        original_func: The original tool function
        tool_name: Name of the tool
        operation_type: Type of operation
    
    Returns:
        Logged version of the function
    """
    return log_tool_usage(tool_name, operation_type)(original_func)
