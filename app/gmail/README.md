# Gmail API Integration

This module provides comprehensive Gmail API integration for the FastAPI application.

## Features

- **Message Management**: Send, receive, search, and manage emails
- **Thread Management**: Work with email threads and conversations
- **Label Management**: Manage Gmail labels and categories
- **Draft Management**: Create and manage draft messages
- **Attachment Support**: Handle email attachments
- **Advanced Search**: Powerful email search capabilities
- **OAuth2 Authentication**: Secure Google OAuth2 integration

## Setup

### 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Create OAuth 2.0 Client ID credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Desktop application" (recommended) or "Web application"
   - **Important**: Add `http://localhost:8080` to "Authorized redirect URIs"
   - Download the credentials JSON file
   - **Important**: This is OAuth 2.0 Client ID credentials, not a service account key

5. Configure OAuth consent screen:
   - Go to "APIs & Services" → "OAuth consent screen"
   - Choose "External" user type (unless you have Google Workspace)
   - Fill in required fields (App name, User support email, Developer contact)
   - Add your Gmail address to "Test users" section
   - Save the configuration

### 2. Environment Configuration

Set the following environment variables (optional):

```bash
# Path to your OAuth 2.0 Client ID credentials file (optional)
# Defaults to app/gmail/credentials.json
GMAIL_CREDENTIALS_FILE=path/to/credentials.json

# Path to store the OAuth2 token (optional, defaults to token.pickle)
GMAIL_TOKEN_FILE=path/to/token.pickle
```

**Note**: The easiest setup is to simply place your `credentials.json` file in the `app/gmail/` directory. The application will automatically detect and use it.

### 3. First Run Authentication

On first run, the application will:
1. Open a browser window for Google OAuth2 authentication
2. Ask you to authorize the application
3. Save the authentication token for future use

**Notes**: 
- If you get a "redirect_uri_mismatch" error, make sure you've added `http://localhost:8080` to the Authorized redirect URIs in your Google Cloud Console OAuth 2.0 Client ID settings.
- If you get an "Access blocked" error, add your Gmail address to the "Test users" section in the OAuth consent screen.

## API Endpoints

### Profile
- `GET /gmail/profile` - Get Gmail profile information

### Messages
- `GET /gmail/messages` - Get messages with optional query
- `GET /gmail/messages/{message_id}` - Get specific message
- `POST /gmail/messages/send` - Send a message
- `POST /gmail/messages/{message_id}/labels` - Modify message labels
- `DELETE /gmail/messages/{message_id}` - Delete a message

### Threads
- `GET /gmail/threads` - Get threads with optional query
- `GET /gmail/threads/{thread_id}` - Get specific thread

### Labels
- `GET /gmail/labels` - Get all labels

### Drafts
- `GET /gmail/drafts` - Get all drafts
- `POST /gmail/drafts` - Create a draft

### Search
- `POST /gmail/search` - Advanced message search

### Convenience Endpoints
- `GET /gmail/unread` - Get unread messages
- `GET /gmail/starred` - Get starred messages
- `GET /gmail/important` - Get important messages
- `GET /gmail/sent` - Get sent messages
- `GET /gmail/inbox` - Get inbox messages
- `GET /gmail/from/{email}` - Get messages from specific sender
- `GET /gmail/to/{email}` - Get messages to specific recipient
- `GET /gmail/subject/{subject}` - Get messages with specific subject
- `GET /gmail/attachments` - Get messages with attachments
- `GET /gmail/today` - Get today's messages
- `GET /gmail/this-week` - Get this week's messages
- `GET /gmail/this-month` - Get this month's messages

## Usage Examples

### Send an Email

```python
from gmail.models import SendMessageRequest, CreateMessageRequest

# Create message request
message_request = CreateMessageRequest(
    to=["recipient@example.com"],
    subject="Test Email",
    body_text="This is a test email from the Gmail API."
)

# Send message
send_request = SendMessageRequest(message=message_request)
response = await gmail_service.send_message(send_request)
```

### Search Messages

```python
# Search for unread messages from a specific sender
response = await gmail_service.get_messages(
    query="is:unread from:sender@example.com",
    max_results=20
)
```

### Get Message with Attachments

```python
# Get a specific message
response = await gmail_service.get_message("message_id_here")
message = response.data

# Check for attachments
if message.attachments:
    for attachment in message.attachments:
        print(f"Attachment: {attachment.filename} ({attachment.size} bytes)")
```

## Gmail Search Query Syntax

The Gmail API supports powerful search queries:

- `from:email@example.com` - Messages from specific sender
- `to:email@example.com` - Messages to specific recipient
- `subject:keyword` - Messages with keyword in subject
- `is:unread` - Unread messages
- `is:read` - Read messages
- `is:starred` - Starred messages
- `is:important` - Important messages
- `has:attachment` - Messages with attachments
- `in:inbox` - Messages in inbox
- `in:sent` - Sent messages
- `in:trash` - Messages in trash
- `newer_than:1d` - Messages newer than 1 day
- `older_than:1w` - Messages older than 1 week
- `after:2023/1/1` - Messages after specific date
- `before:2023/12/31` - Messages before specific date

## Error Handling

All API responses follow the `GmailResponse` model:

```python
{
    "success": bool,
    "message": str,
    "data": any  # Optional response data
}
```

## Rate Limits

The Gmail API has rate limits:
- 1,000,000 quota units per day
- 250 quota units per user per 100 seconds

Each API call consumes quota units based on the operation type.

## Security Notes

- Store credentials securely
- Use environment variables for sensitive configuration
- Regularly rotate OAuth2 tokens
- Implement proper error handling for authentication failures
- Consider implementing rate limiting in your application

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Ensure credentials file is valid and accessible
2. **Permission Errors**: Check OAuth2 scopes in Google Cloud Console
3. **Rate Limit Errors**: Implement exponential backoff for retries
4. **Token Expiry**: Tokens are automatically refreshed, but manual re-authentication may be required
5. **Redirect URI Mismatch**: Add `http://localhost:8080` to Authorized redirect URIs in Google Cloud Console
6. **Access Blocked**: Add your Gmail address to "Test users" in OAuth consent screen

### Error Troubleshooting

#### "Client secrets must be for a web or installed app"
- **Cause**: Using wrong credential type (API key or service account)
- **Solution**: 
  1. Go to Google Cloud Console > APIs & Services > Credentials
  2. Create Credentials > OAuth 2.0 Client ID
  3. Choose "Desktop application"
  4. Download the credentials.json file

#### "redirect_uri_mismatch"
- **Cause**: Redirect URI in Google Cloud Console doesn't match the one being used
- **Solution**:
  1. Go to Google Cloud Console > APIs & Services > Credentials
  2. Edit your OAuth 2.0 Client ID
  3. Add `http://localhost:8080` to Authorized redirect URIs
  4. Save the changes

#### "Access blocked - App verification required"
- **Cause**: OAuth app is in "Testing" mode and requires Google verification
- **Solution**:
  1. Go to Google Cloud Console > APIs & Services > OAuth consent screen
  2. Scroll to "Test users" section
  3. Add your Gmail address as a test user
  4. Save changes
  5. OR publish your app (requires Google verification)

#### "Service account credentials detected"
- **Cause**: Using service account credentials instead of OAuth 2.0 Client ID
- **Solution**:
  1. Go to Google Cloud Console > APIs & Services > Credentials
  2. Create Credentials > OAuth 2.0 Client ID
  3. Choose "Desktop application"
  4. Download the credentials.json file

#### "Invalid credentials file format"
- **Cause**: Credentials file doesn't contain proper OAuth 2.0 Client ID structure
- **Solution**: Ensure the file contains either 'installed' or 'web' key structure

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.getLogger('gmail').setLevel(logging.DEBUG)
```
