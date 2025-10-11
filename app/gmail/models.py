from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageImportance(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

class MessageStatus(str, Enum):
    UNREAD = "UNREAD"
    READ = "READ"
    STARRED = "STARRED"
    IMPORTANT = "IMPORTANT"

class Attachment(BaseModel):
    filename: str
    mime_type: str
    size: int
    attachment_id: str

class EmailAddress(BaseModel):
    name: Optional[str] = None
    email: EmailStr

class Message(BaseModel):
    id: str
    thread_id: str
    subject: str
    sender: EmailAddress
    recipients: List[EmailAddress]
    cc: Optional[List[EmailAddress]] = None
    bcc: Optional[List[EmailAddress]] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    attachments: Optional[List[Attachment]] = None
    received_date: datetime
    importance: MessageImportance = MessageImportance.NORMAL
    status: MessageStatus = MessageStatus.UNREAD
    labels: Optional[List[str]] = None

class CreateMessageRequest(BaseModel):
    to: List[EmailStr]
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    subject: str
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None

class SendMessageRequest(BaseModel):
    message: CreateMessageRequest
    thread_id: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 10
    page_token: Optional[str] = None
    text_only: Optional[bool] = False

class Label(BaseModel):
    id: str
    name: str
    type: str
    messages_total: Optional[int] = None
    messages_unread: Optional[int] = None
    threads_total: Optional[int] = None
    threads_unread: Optional[int] = None

class Thread(BaseModel):
    id: str
    messages: List[Message]
    snippet: Optional[str] = None
    history_id: Optional[str] = None

class Draft(BaseModel):
    id: str
    message: Message
    created_date: datetime

class CreateDraftRequest(BaseModel):
    message: CreateMessageRequest

class GmailResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
