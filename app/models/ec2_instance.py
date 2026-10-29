"""
EC2 Instance MongoDB Model
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId


class EC2Instance(BaseModel):
    """EC2 Instance model for MongoDB storage"""

    # Primary identifier
    instance_id: str = Field(..., description="EC2 Instance ID")

    # Instance details
    instance_type: str = Field(..., description="EC2 Instance Type")
    region: str = Field(..., description="AWS Region")
    state: str = Field(..., description="Instance State")

    # Network information
    public_ip: Optional[str] = Field(None, description="Public IP Address")
    private_ip: Optional[str] = Field(None, description="Private IP Address")

    # Instance metadata
    instance_name: Optional[str] = Field(None, description="Instance Name from Tags")
    ami_id: Optional[str] = Field(None, description="AMI ID")
    key_name: Optional[str] = Field(None, description="Key Pair Name")

    # Timing information
    launch_time: datetime = Field(..., description="Instance Launch Time")
    runtime_seconds: Optional[float] = Field(None, description="Runtime in seconds")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last Update Time")

    # Additional metadata
    tags: Optional[Dict[str, str]] = Field(None, description="Instance Tags")
    security_groups: Optional[list] = Field(None, description="Security Groups")
    vpc_id: Optional[str] = Field(None, description="VPC ID")
    subnet_id: Optional[str] = Field(None, description="Subnet ID")

    # MongoDB specific
    id: Optional[ObjectId] = Field(None, alias="_id")

    class Config:
        """Pydantic configuration"""
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if '_id' in data and data['_id'] is None:
            del data['_id']
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EC2Instance':
        """Create instance from dictionary"""
        if '_id' in data:
            data['id'] = ObjectId(data['_id'])
            del data['_id']
        return cls(**data)


class EC2InstanceUpdate(BaseModel):
    """Model for updating EC2 instance data"""

    instance_type: Optional[str] = None
    region: Optional[str] = None
    state: Optional[str] = None
    public_ip: Optional[str] = None
    private_ip: Optional[str] = None
    instance_name: Optional[str] = None
    ami_id: Optional[str] = None
    key_name: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    security_groups: Optional[list] = None
    vpc_id: Optional[str] = None
    subnet_id: Optional[str] = None
    runtime_seconds: Optional[float] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
