"""Gmail MCP Server - Multi-account Gmail access for Claude."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server.fastmcp import FastMCP
import db, auth, gmail_client

mcp = FastMCP("gmail-multi")

@mcp.tool()
def list_accounts() -> str:
    """List all authenticated Gmail accounts."""
    accounts = db.list_accounts()
    if not accounts:
        return "No accounts authenticated. Use add_account() to add one."
    return "Authenticated accounts:\n" + "\n".join(f"- {a}" for a in accounts)

@mcp.tool()
def add_account(email: str) -> str:
    """Add and authenticate a new Gmail account. Opens browser for Google sign-in."""
    try:
        auth.authenticate_account(email)
        return f"Successfully authenticated {email}"
    except Exception as e:
        return f"Authentication failed: {str(e)}"

@mcp.tool()
def remove_account(email: str) -> str:
    """Remove an authenticated account."""
    if db.remove_account(email):
        return f"Removed {email}"
    return f"Account {email} not found"

@mcp.tool()
def search_emails(account: str, query: str, max_results: int = 10) -> str:
    """Search emails in a Gmail account. Use Gmail search syntax like 'is:unread', 'from:someone@example.com'."""
    creds = auth.get_credentials(account)
    if not creds:
        return f"Account {account} not authenticated. Use add_account() first."
    try:
        messages = gmail_client.search_messages(creds, query, max_results)
        if not messages:
            return f"No emails found matching: {query}"
        result = f"Found {len(messages)} emails:\n\n"
        for msg in messages:
            result += f"ID: {msg['id']}\nSubject: {msg['subject']}\nFrom: {msg['from']}\nDate: {msg['date']}\nPreview: {msg['snippet']}...\n" + "-"*40 + "\n"
        return result
    except Exception as e:
        return f"Error searching emails: {str(e)}"

@mcp.tool()
def read_email(account: str, message_id: str) -> str:
    """Read the full content of an email by its ID."""
    creds = auth.get_credentials(account)
    if not creds:
        return f"Account {account} not authenticated. Use add_account() first."
    try:
        msg = gmail_client.get_message(creds, message_id)
        result = f"Subject: {msg['subject']}\nFrom: {msg['from']}\nTo: {msg['to']}\n"
        if msg['cc']: result += f"CC: {msg['cc']}\n"
        result += f"Date: {msg['date']}\nLabels: {', '.join(msg['labels'])}\n\n--- Body ---\n\n{msg['body']}"
        return result
    except Exception as e:
        return f"Error reading email: {str(e)}"

@mcp.tool()
def send_email(account: str, to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> str:
    """Send an email from a Gmail account."""
    creds = auth.get_credentials(account)
    if not creds:
        return f"Account {account} not authenticated. Use add_account() first."
    try:
        result = gmail_client.send_message(creds, to, subject, body, cc, bcc)
        return f"Email sent successfully! Message ID: {result['id']}"
    except Exception as e:
        return f"Error sending email: {str(e)}"

@mcp.tool()
def get_labels(account: str) -> str:
    """Get all labels/folders for a Gmail account."""
    creds = auth.get_credentials(account)
    if not creds:
        return f"Account {account} not authenticated. Use add_account() first."
    try:
        labels = gmail_client.get_labels(creds)
        return "Labels:\n" + "\n".join(f"- {l['name']} (ID: {l['id']})" for l in labels)
    except Exception as e:
        return f"Error getting labels: {str(e)}"

@mcp.tool()
def archive_email(account: str, message_id: str) -> str:
    """Archive an email (remove from inbox)."""
    creds = auth.get_credentials(account)
    if not creds:
        return f"Account {account} not authenticated. Use add_account() first."
    try:
        gmail_client.modify_labels(creds, message_id, remove_labels=["INBOX"])
        return f"Email {message_id} archived."
    except Exception as e:
        return f"Error archiving email: {str(e)}"

@mcp.tool()
def mark_as_read(account: str, message_id: str) -> str:
    """Mark an email as read."""
    creds = auth.get_credentials(account)
    if not creds:
        return f"Account {account} not authenticated."
    try:
        gmail_client.modify_labels(creds, message_id, remove_labels=["UNREAD"])
        return f"Email {message_id} marked as read."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def mark_as_unread(account: str, message_id: str) -> str:
    """Mark an email as unread."""
    creds = auth.get_credentials(account)
    if not creds:
        return f"Account {account} not authenticated."
    try:
        gmail_client.modify_labels(creds, message_id, add_labels=["UNREAD"])
        return f"Email {message_id} marked as unread."
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    mcp.run()

if __name__ == "__main__":
    main()
    
