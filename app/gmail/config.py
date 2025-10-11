import os
import json
from typing import Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GmailConfig:
    def __init__(self):
        self.SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/gmail.insert',
            'https://www.googleapis.com/auth/gmail.labels'
        ]
        
        # Default to gmail/credentials.json
        default_path = os.path.join(os.path.dirname(__file__), "credentials.json")
        if os.path.exists(default_path):
            self.CREDENTIALS_FILE = default_path
        else:
            self.CREDENTIALS_FILE = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
        
        self.API_NAME = 'gmail'
        self.API_VERSION = 'v1'
    
    def _validate_credentials_file(self) -> bool:
        """Validate that the credentials file is a proper OAuth 2.0 Client ID file."""
        try:
            with open(self.CREDENTIALS_FILE, 'r') as f:
                creds_data = json.load(f)
            
            if 'installed' in creds_data or 'web' in creds_data:
                return True
            elif 'type' in creds_data and creds_data['type'] == 'service_account':
                raise Exception("Service account credentials detected! Gmail API requires OAuth 2.0 Client ID credentials.")
            else:
                raise Exception("Invalid credentials file format! Expected OAuth 2.0 Client ID credentials.")
                
        except json.JSONDecodeError:
            raise Exception("Invalid JSON format in credentials file!")
        except Exception as e:
            raise Exception(f"Error reading credentials file: {e}")
        
    def get_credentials(self) -> Optional[Credentials]:
        """Get valid user credentials from storage or prompt user to log in."""
        if not os.path.exists(self.CREDENTIALS_FILE):
            raise Exception(f"Credentials file not found: {self.CREDENTIALS_FILE}")
        
        # Validate credentials file format
        self._validate_credentials_file()
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.CREDENTIALS_FILE, self.SCOPES)
            creds = flow.run_local_server(port=8080)
            return creds
        except Exception as e:
            raise Exception(f"OAuth flow failed: {e}")
    
    def get_service(self):
        """Get Gmail service instance."""
        creds = self.get_credentials()
        if not creds:
            raise Exception("Failed to obtain valid credentials")
        
        try:
            service = build(self.API_NAME, self.API_VERSION, credentials=creds)
            return service
        except Exception as e:
            raise Exception(f"Failed to build Gmail service: {e}")
    
    def is_configured(self) -> bool:
        """Check if Gmail API is properly configured."""
        return os.path.exists(self.CREDENTIALS_FILE)
