from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional

class Note(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    subject: str
    description: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
