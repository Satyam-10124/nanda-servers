#!/usr/bin/env python3
"""
Email Integration MCP Server for NANDA

Enables NANDA agents to send and manage emails via Gmail API.
"""

from mcp.server.fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
import os
import pickle
from typing import Optional, List

mcp = FastMCP("email-integration")

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    """Authenticate and return Gmail API service"""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)


@mcp.tool()
def send_email(to: str, subject: str, body: str, body_type: str = "plain") -> dict:
    """
    Send an email via Gmail
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        body_type: "plain" or "html" (default: plain)
    
    Returns:
        Status and message ID
    """
    try:
        service = get_gmail_service()
        
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        
        msg = MIMEText(body, body_type)
        message.attach(msg)
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_message = {'raw': raw}
        
        result = service.users().messages().send(
            userId='me', body=send_message).execute()
        
        return {
            "success": True,
            "message_id": result['id'],
            "to": to
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def send_email_with_attachment(
    to: str,
    subject: str,
    body: str,
    file_path: str
) -> dict:
    """
    Send email with file attachment
    
    Args:
        to: Recipient email
        subject: Email subject
        body: Email body
        file_path: Path to file to attach
    
    Returns:
        Status and message ID
    """
    try:
        service = get_gmail_service()
        
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        
        message.attach(MIMEText(body, 'plain'))
        
        # Attach file
        with open(file_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {os.path.basename(file_path)}'
        )
        message.attach(part)
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_message = {'raw': raw}
        
        result = service.users().messages().send(
            userId='me', body=send_message).execute()
        
        return {
            "success": True,
            "message_id": result['id'],
            "to": to,
            "attachment": os.path.basename(file_path)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def read_inbox(max_results: int = 10, query: str = "") -> dict:
    """
    Read emails from inbox
    
    Args:
        max_results: Maximum emails to return (default: 10)
        query: Gmail search query (e.g., "is:unread", "from:example@email.com")
    
    Returns:
        List of emails with details
    """
    try:
        service = get_gmail_service()
        
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q=query
        ).execute()
        
        messages = results.get('messages', [])
        
        emails = []
        for msg in messages:
            message = service.users().messages().get(
                userId='me', id=msg['id']).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
            
            emails.append({
                "id": message['id'],
                "subject": subject,
                "from": from_email,
                "date": date,
                "snippet": message['snippet']
            })
        
        return {
            "success": True,
            "count": len(emails),
            "emails": emails
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def search_emails(query: str, max_results: int = 20) -> dict:
    """
    Search emails using Gmail query syntax
    
    Args:
        query: Gmail search query (e.g., "from:boss subject:urgent")
        max_results: Max results to return
    
    Returns:
        List of matching emails
    """
    try:
        service = get_gmail_service()
        
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q=query
        ).execute()
        
        messages = results.get('messages', [])
        
        emails = []
        for msg in messages:
            message = service.users().messages().get(
                userId='me', id=msg['id']).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            
            emails.append({
                "id": message['id'],
                "subject": subject,
                "from": from_email,
                "snippet": message['snippet']
            })
        
        return {
            "success": True,
            "query": query,
            "count": len(emails),
            "emails": emails
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def mark_as_read(message_id: str) -> dict:
    """
    Mark an email as read
    
    Args:
        message_id: Gmail message ID
    
    Returns:
        Success status
    """
    try:
        service = get_gmail_service()
        
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        
        return {
            "success": True,
            "message_id": message_id,
            "status": "marked_as_read"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def delete_email(message_id: str) -> dict:
    """
    Delete an email (move to trash)
    
    Args:
        message_id: Gmail message ID
    
    Returns:
        Success status
    """
    try:
        service = get_gmail_service()
        
        service.users().messages().trash(
            userId='me',
            id=message_id
        ).execute()
        
        return {
            "success": True,
            "message_id": message_id,
            "status": "deleted"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    print("🚀 Starting Email Integration MCP Server")
    print("📧 Gmail API authentication required")
    print()
    mcp.run()
