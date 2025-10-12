#!/usr/bin/env python3
"""
Activity Logger for EC2Forge
Custom logging handler that stores logs in MongoDB with structured format
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from core.mongodb import get_database
from core.log_config import logger
from models.activity_log import ActivityLog


class MongoDBLogHandler(logging.Handler):
    """Custom logging handler that stores logs in MongoDB"""
    
    def __init__(self, collection_name: str = "activity_logs"):
        super().__init__()
        self.collection_name = collection_name
        self._collection = None
        
    @property
    def collection(self):
        """Get MongoDB collection, initialize if needed"""
        if self._collection is None:
            database = get_database()
            if database is not None:
                self._collection = database[self.collection_name]
            else:
                logger.error("Database not available for logging")
        return self._collection
    
    def emit(self, record: logging.LogRecord):
        """Emit a log record to MongoDB"""
        try:
            # Extract custom attributes from log record
            tool_name = getattr(record, 'tool_name', 'unknown')
            operation_type = getattr(record, 'operation_type', 'general')
            session_id = getattr(record, 'session_id', None)
            user_id = getattr(record, 'user_id', None)
            details = getattr(record, 'details', {})
            execution_time_ms = getattr(record, 'execution_time_ms', None)
            status = getattr(record, 'status', 'in_progress')
            metadata = getattr(record, 'metadata', {})
            print(f"================Logging the logs into the collection =============>")
            
            # Create log entry
            log_entry = ActivityLog(
                timestamp=datetime.now(),
                date=datetime.now().strftime("%Y-%m-%d"),
                log_level=record.levelname,
                tool_name=tool_name,
                operation_type=operation_type,
                session_id=session_id,
                user_id=user_id,
                message=record.getMessage(),
                details=details,
                execution_time_ms=execution_time_ms,
                status=status,
                metadata=metadata
            )
            
            # Insert into MongoDB (async operation in sync context)
            if self.collection is not None:
                print(f"================Logging the logs into the collection if=============>")
                # Run async operation in thread pool to avoid event loop conflicts
                import threading
                
                def insert_log():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            loop.run_until_complete(
                                self.collection.insert_one(log_entry.model_dump(by_alias=True, exclude={'id'}))
                            )
                        finally:
                            loop.close()
                    except Exception as e:
                        print(f"Error in thread: {e}")
                
                # Run in separate thread to avoid event loop conflicts
                thread = threading.Thread(target=insert_log)
                thread.daemon = True
                thread.start()
                    
        except Exception as e:
            # Don't let logging errors break the application
            logger.error(f"Error storing log in MongoDB: {e}")


class ActivityLogger:
    """Activity Logger utility class"""
    
    def __init__(self, name: str = "ec2forge"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Add MongoDB handler if not already present
        if not any(isinstance(h, MongoDBLogHandler) for h in self.logger.handlers):
            mongo_handler = MongoDBLogHandler()
            mongo_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(mongo_handler)
    
    def log_operation_start(self, 
                           tool_name: str, 
                           operation_type: str, 
                           message: str,
                           session_id: Optional[str] = None,
                           user_id: Optional[str] = None,
                           details: Optional[Dict[str, Any]] = None,
                           metadata: Optional[Dict[str, Any]] = None):
        """Log the start of an operation"""
        extra = {
            'tool_name': tool_name,
            'operation_type': operation_type,
            'session_id': session_id,
            'user_id': user_id,
            'details': details or {},
            'status': 'in_progress',
            'metadata': metadata or {}
        }
        self.logger.info(message, extra=extra)
    
    def log_operation_success(self, 
                             tool_name: str, 
                             operation_type: str, 
                             message: str,
                             execution_time_ms: int,
                             session_id: Optional[str] = None,
                             user_id: Optional[str] = None,
                             details: Optional[Dict[str, Any]] = None,
                             metadata: Optional[Dict[str, Any]] = None):
        """Log successful completion of an operation"""
        extra = {
            'tool_name': tool_name,
            'operation_type': operation_type,
            'session_id': session_id,
            'user_id': user_id,
            'details': details or {},
            'execution_time_ms': execution_time_ms,
            'status': 'success',
            'metadata': metadata or {}
        }
        self.logger.info(message, extra=extra)
    
    def log_operation_error(self, 
                           tool_name: str, 
                           operation_type: str, 
                           message: str,
                           error_details: Dict[str, Any],
                           session_id: Optional[str] = None,
                           user_id: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None):
        """Log an error during operation"""
        extra = {
            'tool_name': tool_name,
            'operation_type': operation_type,
            'session_id': session_id,
            'user_id': user_id,
            'details': error_details,
            'status': 'failure',
            'metadata': metadata or {}
        }
        self.logger.error(message, extra=extra)
    
    def log_operation_complete(self, 
                              tool_name: str, 
                              operation_type: str, 
                              message: str,
                              execution_time_ms: int = None,
                              status: str = "success",
                              session_id: Optional[str] = None,
                              user_id: Optional[str] = None,
                              details: Optional[Dict[str, Any]] = None,
                              metadata: Optional[Dict[str, Any]] = None):
        """Log completion of an operation (success or failure)"""
        extra = {
            'tool_name': tool_name,
            'operation_type': operation_type,
            'session_id': session_id,
            'user_id': user_id,
            'details': details or {},
            'execution_time_ms': execution_time_ms,
            'status': status,
            'metadata': metadata or {}
        }
        
        if status == "success":
            self.logger.info(message, extra=extra)
        else:
            self.logger.error(message, extra=extra)
    
    def log_tool_registration(self, tool_name: str, message: str):
        """Log tool registration events"""
        extra = {
            'tool_name': tool_name,
            'operation_type': 'tool_registration',
            'status': 'success'
        }
        self.logger.debug(message, extra=extra)
    
    def log_tool_execution(self, 
                          tool_name: str, 
                          operation_type: str, 
                          message: str,
                          execution_time_ms: Optional[int] = None,
                          session_id: Optional[str] = None,
                          user_id: Optional[str] = None,
                          details: Optional[Dict[str, Any]] = None,
                          metadata: Optional[Dict[str, Any]] = None):
        """Log tool execution events"""
        extra = {
            'tool_name': tool_name,
            'operation_type': operation_type,
            'session_id': session_id,
            'user_id': user_id,
            'details': details or {},
            'execution_time_ms': execution_time_ms,
            'status': 'success',
            'metadata': metadata or {}
        }
        self.logger.debug(message, extra=extra)


# Global activity logger instance
activity_logger = ActivityLogger()
