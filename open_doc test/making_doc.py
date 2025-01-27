from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import json
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/documents']

def get_credentials():
    creds = None
    # Load credentials from .env
    creds_json = json.loads(os.getenv('GOOGLE_CREDENTIALS_JSON'))
    
    flow = InstalledAppFlow.from_client_config(creds_json, SCOPES)
    creds = flow.run_local_server(port=0)
    return creds

def create_doc(title, content):
    """Create a new Google Doc with the given title and content."""
    creds = get_credentials()
    service = build('docs', 'v1', credentials=creds)
    
    # Create a new document
    doc = service.documents().create(body={'title': title}).execute()
    
    # Insert text into the document
    requests = [{
        'insertText': {
            'location': {
                'index': 1
            },
            'text': content
        }
    }]
    
    service.documents().batchUpdate(
        documentId=doc.get('documentId'),
        body={'requests': requests}
    ).execute()
    
    print(f"Created document with ID: {doc.get('documentId')}")
    print(f"View your document at: https://docs.google.com/document/d/{doc.get('documentId')}")

def main():
    title = input("Enter document title: ")
    content = input("Enter document content: ")
    create_doc(title, content)

if __name__ == '__main__':
    main() 