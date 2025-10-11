from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
from .service import GmailService
from .models import (
    CreateMessageRequest, SendMessageRequest, SearchRequest,
    CreateDraftRequest, GmailResponse
)

router = APIRouter()

# Initialize Gmail service
gmail_service = GmailService()

@router.get("/profile", response_model=GmailResponse)
async def get_profile():
    """Get Gmail profile information."""
    return await gmail_service.get_profile()

@router.get("/messages", response_model=GmailResponse)
async def get_messages(
    query: str = Query("", description="Gmail search query"),
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=500),
    page_token: str = Query(None, description="Page token for pagination"),
    text_only: bool = Query(False, description="Return only plain text content (no HTML)")
):
    """Get messages from Gmail."""
    return await gmail_service.get_messages(query, max_results, page_token, text_only)

@router.get("/messages/{message_id}", response_model=GmailResponse)
async def get_message(
    message_id: str,
    text_only: bool = Query(False, description="Return only plain text content (no HTML)")
):
    """Get a specific message by ID."""
    return await gmail_service.get_message(message_id, text_only)

@router.post("/messages/send", response_model=GmailResponse)
async def send_message(request: SendMessageRequest = Body(...)):
    """Send a message."""
    return await gmail_service.send_message(request)

@router.post("/messages/{message_id}/labels", response_model=GmailResponse)
async def modify_message_labels(
    message_id: str,
    add_labels: Optional[List[str]] = Body(None),
    remove_labels: Optional[List[str]] = Body(None)
):
    """Modify labels on a message."""
    return await gmail_service.modify_message_labels(message_id, add_labels, remove_labels)

@router.delete("/messages/{message_id}", response_model=GmailResponse)
async def delete_message(message_id: str):
    """Delete a message."""
    return await gmail_service.delete_message(message_id)

@router.get("/labels", response_model=GmailResponse)
async def get_labels():
    """Get all labels."""
    return await gmail_service.get_labels()

@router.get("/label/{label_id}", response_model=GmailResponse)
async def get_messages_by_label(
    label_id: str,
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=500),
    text_only: bool = Query(False, description="Return only plain text content (no HTML)")
):
    """Get messages with a specific label."""
    return await gmail_service.get_messages(query=f"label:{label_id}", max_results=max_results, text_only=text_only)

@router.get("/threads", response_model=GmailResponse)
async def get_threads(
    query: str = Query("", description="Gmail search query"),
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=500),
    page_token: str = Query(None, description="Page token for pagination"),
    text_only: bool = Query(False, description="Return only plain text content (no HTML)")
):
    """Get threads from Gmail."""
    return await gmail_service.get_threads(query, max_results, page_token, text_only)

@router.get("/threads/{thread_id}", response_model=GmailResponse)
async def get_thread(thread_id: str):
    """Get a specific thread by ID."""
    return await gmail_service.get_threads(query=f"thread:{thread_id}")

@router.get("/drafts", response_model=GmailResponse)
async def get_drafts(
    text_only: bool = Query(False, description="Return only plain text content (no HTML)")
):
    """Get all drafts."""
    return await gmail_service.get_drafts(text_only)

@router.post("/drafts", response_model=GmailResponse)
async def create_draft(request: CreateDraftRequest = Body(...)):
    """Create a draft message."""
    return await gmail_service.create_draft(request)

@router.post("/search", response_model=GmailResponse)
async def search_messages(request: SearchRequest = Body(...)):
    """Search messages with advanced query."""
    return await gmail_service.get_messages(
        query=request.query,
        max_results=request.max_results or 10,
        page_token=request.page_token,
        text_only=request.text_only or False
    )

# Convenience endpoints for common operations
@router.get("/unread", response_model=GmailResponse)
async def get_unread_messages(
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=500),
    text_only: bool = Query(False, description="Return only plain text content (no HTML)")
):
    """Get unread messages."""
    return await gmail_service.get_messages(query="is:unread", max_results=max_results, text_only=text_only)

@router.get("/starred", response_model=GmailResponse)
async def get_starred_messages(
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=500),
    text_only: bool = Query(False, description="Return only plain text content (no HTML)")
):
    """Get starred messages."""
    return await gmail_service.get_messages(query="is:starred", max_results=max_results, text_only=text_only)

@router.get("/important", response_model=GmailResponse)
async def get_important_messages(
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=500),
    text_only: bool = Query(False, description="Return only plain text content (no HTML)")
):
    """Get important messages."""
    return await gmail_service.get_messages(query="is:important", max_results=max_results, text_only=text_only)

@router.get("/sent", response_model=GmailResponse)
async def get_sent_messages(
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=500),
    text_only: bool = Query(False, description="Return only plain text content (no HTML)")
):
    """Get sent messages."""
    return await gmail_service.get_messages(query="in:sent", max_results=max_results, text_only=text_only)

@router.get("/inbox", response_model=GmailResponse)
async def get_inbox_messages(
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=500),
    text_only: bool = Query(False, description="Return only plain text content (no HTML)")
):
    """Get inbox messages."""
    return await gmail_service.get_messages(query="in:inbox", max_results=max_results, text_only=text_only)

@router.get("/from/{email}", response_model=GmailResponse)
async def get_messages_from(
    email: str,
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=500),
    text_only: bool = Query(False, description="Return only plain text content (no HTML)")
):
    """Get messages from a specific email address."""
    return await gmail_service.get_messages(query=f"from:{email}", max_results=max_results, text_only=text_only)

@router.get("/to/{email}", response_model=GmailResponse)
async def get_messages_to(
    email: str,
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=500),
    text_only: bool = Query(False, description="Return only plain text content (no HTML)")
):
    """Get messages to a specific email address."""
    return await gmail_service.get_messages(query=f"to:{email}", max_results=max_results, text_only=text_only)

@router.get("/subject/{subject}", response_model=GmailResponse)
async def get_messages_by_subject(
    subject: str,
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=500),
    text_only: bool = Query(False, description="Return only plain text content (no HTML)")
):
    """Get messages with a specific subject."""
    return await gmail_service.get_messages(query=f'subject:"{subject}"', max_results=max_results, text_only=text_only)

@router.get("/attachments", response_model=GmailResponse)
async def get_messages_with_attachments(
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=500),
    text_only: bool = Query(False, description="Return only plain text content (no HTML)")
):
    """Get messages with attachments."""
    return await gmail_service.get_messages(query="has:attachment", max_results=max_results, text_only=text_only)

@router.get("/today", response_model=GmailResponse)
async def get_todays_messages(
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=500),
    text_only: bool = Query(False, description="Return only plain text content (no HTML)")
):
    """Get today's messages."""
    return await gmail_service.get_messages(query="newer_than:1d", max_results=max_results, text_only=text_only)

@router.get("/this-week", response_model=GmailResponse)
async def get_this_weeks_messages(
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=500),
    text_only: bool = Query(False, description="Return only plain text content (no HTML)")
):
    """Get this week's messages."""
    return await gmail_service.get_messages(query="newer_than:7d", max_results=max_results, text_only=text_only)

@router.get("/this-month", response_model=GmailResponse)
async def get_this_months_messages(
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=500),
    text_only: bool = Query(False, description="Return only plain text content (no HTML)")
):
    """Get this month's messages."""
    return await gmail_service.get_messages(query="newer_than:30d", max_results=max_results, text_only=text_only)
