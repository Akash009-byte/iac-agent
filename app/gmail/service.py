import base64
import email
import json
import logging
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .config import GmailConfig
from .models import (
    Message, EmailAddress, Attachment, Label, Thread, Draft,
    CreateMessageRequest, SendMessageRequest, SearchRequest,
    CreateDraftRequest, GmailResponse, MessageImportance, MessageStatus
)

logger = logging.getLogger(__name__)

class GmailService:
    def __init__(self):
        self.config = GmailConfig()
        self.service = None
    
    def _get_service(self):
        """Get Gmail service instance."""
        if not self.service:
            self.service = self.config.get_service()
        return self.service
    
    def _parse_email_addresses(self, header_value: str) -> List[EmailAddress]:
        """Parse email addresses from header value."""
        if not header_value:
            return []
        
        addresses = []
        for addr in email.utils.getaddresses([header_value]):
            name, email_addr = addr
            addresses.append(EmailAddress(name=name if name else None, email=email_addr))
        return addresses
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML content to plain text."""
        if not html_content:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def _parse_message(self, gmail_message: Dict[str, Any], text_only: bool = False) -> Message:
        """Parse Gmail message format to our Message model."""
        payload = gmail_message.get('payload', {})
        headers = payload.get('headers', [])
        
        # Extract headers
        header_dict = {h['name'].lower(): h['value'] for h in headers}
        
        # Parse addresses
        sender = self._parse_email_addresses(header_dict.get('from', ''))
        to = self._parse_email_addresses(header_dict.get('to', ''))
        cc = self._parse_email_addresses(header_dict.get('cc', ''))
        bcc = self._parse_email_addresses(header_dict.get('bcc', ''))
        
        # Extract body
        body_text = None
        body_html = None
        
        if 'parts' in payload:
            for part in payload['parts']:
                mime_type = part.get('mimeType', '')
                if mime_type == 'text/plain' and not body_text:
                    if 'data' in part.get('body', {}):
                        body_text = base64.urlsafe_b64decode(
                            part['body']['data'] + '=='
                        ).decode('utf-8')
                elif mime_type == 'text/html' and not body_html:
                    if 'data' in part.get('body', {}):
                        body_html = base64.urlsafe_b64decode(
                            part['body']['data'] + '=='
                        ).decode('utf-8')
        else:
            if payload.get('mimeType') == 'text/plain':
                if 'data' in payload.get('body', {}):
                    body_text = base64.urlsafe_b64decode(
                        payload['body']['data'] + '=='
                    ).decode('utf-8')
            elif payload.get('mimeType') == 'text/html':
                if 'data' in payload.get('body', {}):
                    body_html = base64.urlsafe_b64decode(
                        payload['body']['data'] + '=='
                    ).decode('utf-8')
        
        # Handle text_only mode
        if text_only:
            # If we have HTML but no plain text, convert HTML to text
            if body_html and not body_text:
                body_text = self._html_to_text(body_html)
            # Always return None for HTML in text_only mode
            body_html = None
        
        # Parse attachments
        attachments = []
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('filename') and part.get('body', {}).get('attachmentId'):
                    attachments.append(Attachment(
                        filename=part['filename'],
                        mime_type=part.get('mimeType', ''),
                        size=part.get('body', {}).get('size', 0),
                        attachment_id=part['body']['attachmentId']
                    ))
        
        # Parse date
        date_str = header_dict.get('date', '')
        received_date = datetime.now()
        if date_str:
            try:
                received_date = email.utils.parsedate_to_datetime(date_str)
            except:
                pass
        
        return Message(
            id=gmail_message['id'],
            thread_id=gmail_message['threadId'],
            subject=header_dict.get('subject', ''),
            sender=sender[0] if sender else EmailAddress(email=''),
            recipients=to,
            cc=cc if cc else None,
            bcc=bcc if bcc else None,
            body_text=body_text,
            body_html=body_html if not text_only else None,
            attachments=attachments if attachments else None,
            received_date=received_date,
            labels=gmail_message.get('labelIds', [])
        )
    
    async def get_messages(self, query: str = '', max_results: int = 10, page_token: str = None, text_only: bool = False) -> GmailResponse:
        """Get messages from Gmail."""
        try:
            service = self._get_service()
            
            # Get message list
            list_params = {
                'userId': 'me',
                'maxResults': max_results
            }
            
            if query:
                list_params['q'] = query
            if page_token:
                list_params['pageToken'] = page_token
            
            results = service.users().messages().list(**list_params).execute()
            messages = results.get('messages', [])
            
            if not messages:
                return GmailResponse(
                    success=True,
                    message="No messages found",
                    data={'messages': [], 'next_page_token': results.get('nextPageToken')}
                )
            
            # Get full message details
            parsed_messages = []
            for message in messages:
                try:
                    msg = service.users().messages().get(
                        userId='me', 
                        id=message['id'],
                        format='full'
                    ).execute()
                    parsed_messages.append(self._parse_message(msg, text_only))
                except Exception as e:
                    logger.error(f"Error parsing message {message['id']}: {e}")
                    continue
            
            return GmailResponse(
                success=True,
                message=f"Retrieved {len(parsed_messages)} messages",
                data={
                    'messages': [msg.dict() for msg in parsed_messages],
                    'next_page_token': results.get('nextPageToken')
                }
            )
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return GmailResponse(
                success=False,
                message=f"Gmail API error: {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return GmailResponse(
                success=False,
                message=f"Unexpected error: {e}"
            )
    
    async def get_message(self, message_id: str, text_only: bool = False) -> GmailResponse:
        """Get a specific message by ID."""
        try:
            service = self._get_service()
            message = service.users().messages().get(
                userId='me', 
                id=message_id,
                format='full'
            ).execute()
            
            parsed_message = self._parse_message(message, text_only)
            
            return GmailResponse(
                success=True,
                message="Message retrieved successfully",
                data=parsed_message.dict()
            )
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return GmailResponse(
                success=False,
                message=f"Gmail API error: {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return GmailResponse(
                success=False,
                message=f"Unexpected error: {e}"
            )
    
    async def send_message(self, request: SendMessageRequest) -> GmailResponse:
        """Send a message."""
        try:
            service = self._get_service()
            
            # Create message
            message = MIMEMultipart()
            message['to'] = ', '.join(request.message.to)
            message['subject'] = request.message.subject
            
            if request.message.cc:
                message['cc'] = ', '.join(request.message.cc)
            if request.message.bcc:
                message['bcc'] = ', '.join(request.message.bcc)
            
            # Add body
            if request.message.body_html:
                message.attach(MIMEText(request.message.body_html, 'html'))
            elif request.message.body_text:
                message.attach(MIMEText(request.message.body_text, 'plain'))
            
            # Add attachments
            if request.message.attachments:
                for attachment in request.message.attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment['data'])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment["filename"]}'
                    )
                    message.attach(part)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send message
            send_params = {
                'userId': 'me',
                'body': {'raw': raw_message}
            }
            
            if request.thread_id:
                send_params['body']['threadId'] = request.thread_id
            
            sent_message = service.users().messages().send(**send_params).execute()
            
            return GmailResponse(
                success=True,
                message="Message sent successfully",
                data={'message_id': sent_message['id']}
            )
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return GmailResponse(
                success=False,
                message=f"Gmail API error: {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return GmailResponse(
                success=False,
                message=f"Unexpected error: {e}"
            )
    
    async def get_labels(self) -> GmailResponse:
        """Get all labels."""
        try:
            service = self._get_service()
            results = service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            parsed_labels = []
            for label in labels:
                parsed_labels.append(Label(
                    id=label['id'],
                    name=label['name'],
                    type=label['type'],
                    messages_total=label.get('messagesTotal'),
                    messages_unread=label.get('messagesUnread'),
                    threads_total=label.get('threadsTotal'),
                    threads_unread=label.get('threadsUnread')
                ))
            
            return GmailResponse(
                success=True,
                message=f"Retrieved {len(parsed_labels)} labels",
                data=[label.dict() for label in parsed_labels]
            )
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return GmailResponse(
                success=False,
                message=f"Gmail API error: {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return GmailResponse(
                success=False,
                message=f"Unexpected error: {e}"
            )
    
    async def get_threads(self, query: str = '', max_results: int = 10, page_token: str = None, text_only: bool = False) -> GmailResponse:
        """Get threads from Gmail."""
        try:
            service = self._get_service()
            
            list_params = {
                'userId': 'me',
                'maxResults': max_results
            }
            
            if query:
                list_params['q'] = query
            if page_token:
                list_params['pageToken'] = page_token
            
            results = service.users().threads().list(**list_params).execute()
            threads = results.get('threads', [])
            
            if not threads:
                return GmailResponse(
                    success=True,
                    message="No threads found",
                    data={'threads': [], 'next_page_token': results.get('nextPageToken')}
                )
            
            # Get full thread details
            parsed_threads = []
            for thread in threads:
                try:
                    thread_details = service.users().threads().get(
                        userId='me', 
                        id=thread['id'],
                        format='full'
                    ).execute()
                    
                    messages = []
                    for msg in thread_details.get('messages', []):
                        messages.append(self._parse_message(msg, text_only))
                    
                    parsed_threads.append(Thread(
                        id=thread['id'],
                        messages=messages,
                        snippet=thread_details.get('snippet'),
                        history_id=thread_details.get('historyId')
                    ))
                except Exception as e:
                    logger.error(f"Error parsing thread {thread['id']}: {e}")
                    continue
            
            return GmailResponse(
                success=True,
                message=f"Retrieved {len(parsed_threads)} threads",
                data={
                    'threads': [thread.dict() for thread in parsed_threads],
                    'next_page_token': results.get('nextPageToken')
                }
            )
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return GmailResponse(
                success=False,
                message=f"Gmail API error: {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return GmailResponse(
                success=False,
                message=f"Unexpected error: {e}"
            )
    
    async def create_draft(self, request: CreateDraftRequest) -> GmailResponse:
        """Create a draft message."""
        try:
            service = self._get_service()
            
            # Create message
            message = MIMEMultipart()
            message['to'] = ', '.join(request.message.to)
            message['subject'] = request.message.subject
            
            if request.message.cc:
                message['cc'] = ', '.join(request.message.cc)
            if request.message.bcc:
                message['bcc'] = ', '.join(request.message.bcc)
            
            # Add body
            if request.message.body_html:
                message.attach(MIMEText(request.message.body_html, 'html'))
            elif request.message.body_text:
                message.attach(MIMEText(request.message.body_text, 'plain'))
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Create draft
            draft = service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw_message}}
            ).execute()
            
            return GmailResponse(
                success=True,
                message="Draft created successfully",
                data={'draft_id': draft['id']}
            )
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return GmailResponse(
                success=False,
                message=f"Gmail API error: {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return GmailResponse(
                success=False,
                message=f"Unexpected error: {e}"
            )
    
    async def get_drafts(self, text_only: bool = False) -> GmailResponse:
        """Get all drafts."""
        try:
            service = self._get_service()
            results = service.users().drafts().list(userId='me').execute()
            drafts = results.get('drafts', [])
            
            parsed_drafts = []
            for draft in drafts:
                try:
                    draft_details = service.users().drafts().get(
                        userId='me', 
                        id=draft['id'],
                        format='full'
                    ).execute()
                    
                    message = self._parse_message(draft_details['message'], text_only)
                    parsed_drafts.append(Draft(
                        id=draft['id'],
                        message=message,
                        created_date=datetime.now()  # Gmail doesn't provide creation date in draft list
                    ))
                except Exception as e:
                    logger.error(f"Error parsing draft {draft['id']}: {e}")
                    continue
            
            return GmailResponse(
                success=True,
                message=f"Retrieved {len(parsed_drafts)} drafts",
                data=[draft.dict() for draft in parsed_drafts]
            )
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return GmailResponse(
                success=False,
                message=f"Gmail API error: {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return GmailResponse(
                success=False,
                message=f"Unexpected error: {e}"
            )
    
    async def modify_message_labels(self, message_id: str, add_labels: List[str] = None, remove_labels: List[str] = None) -> GmailResponse:
        """Modify labels on a message."""
        try:
            service = self._get_service()
            
            body = {}
            if add_labels:
                body['addLabelIds'] = add_labels
            if remove_labels:
                body['removeLabelIds'] = remove_labels
            
            modified_message = service.users().messages().modify(
                userId='me',
                id=message_id,
                body=body
            ).execute()
            
            return GmailResponse(
                success=True,
                message="Message labels modified successfully",
                data={'label_ids': modified_message.get('labelIds', [])}
            )
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return GmailResponse(
                success=False,
                message=f"Gmail API error: {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return GmailResponse(
                success=False,
                message=f"Unexpected error: {e}"
            )
    
    async def delete_message(self, message_id: str) -> GmailResponse:
        """Delete a message."""
        try:
            service = self._get_service()
            service.users().messages().delete(userId='me', id=message_id).execute()
            
            return GmailResponse(
                success=True,
                message="Message deleted successfully"
            )
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return GmailResponse(
                success=False,
                message=f"Gmail API error: {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return GmailResponse(
                success=False,
                message=f"Unexpected error: {e}"
            )
    
    async def get_profile(self) -> GmailResponse:
        """Get Gmail profile information."""
        try:
            service = self._get_service()
            profile = service.users().getProfile(userId='me').execute()
            
            return GmailResponse(
                success=True,
                message="Profile retrieved successfully",
                data=profile
            )
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return GmailResponse(
                success=False,
                message=f"Gmail API error: {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return GmailResponse(
                success=False,
                message=f"Unexpected error: {e}"
            )
