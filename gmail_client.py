"""Gmail API client wrapper."""
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build

def get_service(creds):
    return build("gmail", "v1", credentials=creds)

def search_messages(creds, query, max_results=10):
    service = get_service(creds)
    results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    messages = results.get("messages", [])
    summaries = []
    for msg in messages:
        detail = service.users().messages().get(userId="me", id=msg["id"],
            format="metadata", metadataHeaders=["From","To","Subject","Date"]).execute()
        headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
        summaries.append({
            "id": msg["id"], "thread_id": msg.get("threadId"),
            "subject": headers.get("Subject", "(no subject)"),
            "from": headers.get("From", ""), "to": headers.get("To", ""),
            "date": headers.get("Date", ""), "snippet": detail.get("snippet", "")[:100]
        })
    return summaries

def _extract_body(payload):
    if "body" in payload and payload["body"].get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
    if "parts" in payload:
        plain_text = html_text = ""
        for part in payload["parts"]:
            mime = part.get("mimeType", "")
            if mime.startswith("multipart/"):
                result = _extract_body(part)
                if result: return result
            elif mime == "text/plain" and part.get("body", {}).get("data"):
                plain_text = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
            elif mime == "text/html" and part.get("body", {}).get("data") and not html_text:
                html_text = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
        return plain_text or html_text
    return ""

def get_message(creds, message_id):
    service = get_service(creds)
    msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
    return {
        "id": msg["id"], "thread_id": msg.get("threadId"),
        "subject": headers.get("Subject", "(no subject)"),
        "from": headers.get("From", ""), "to": headers.get("To", ""),
        "cc": headers.get("Cc", ""), "date": headers.get("Date", ""),
        "body": _extract_body(msg.get("payload", {})), "labels": msg.get("labelIds", [])
    }

def send_message(creds, to, subject, body, cc="", bcc="", reply_to=""):
    service = get_service(creds)
    message = MIMEMultipart()
    message["to"] = to
    message["subject"] = subject
    if cc: message["cc"] = cc
    if bcc: message["bcc"] = bcc
    if reply_to:
        message["In-Reply-To"] = reply_to
        message["References"] = reply_to
    message.attach(MIMEText(body, "plain"))
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return {"id": result["id"], "thread_id": result.get("threadId"), "status": "sent"}

def get_labels(creds):
    service = get_service(creds)
    results = service.users().labels().list(userId="me").execute()
    return [{"id": l["id"], "name": l["name"], "type": l.get("type", "")}
            for l in results.get("labels", [])]

def modify_labels(creds, message_id, add_labels=None, remove_labels=None):
    service = get_service(creds)
    body = {}
    if add_labels: body["addLabelIds"] = add_labels
    if remove_labels: body["removeLabelIds"] = remove_labels
    result = service.users().messages().modify(userId="me", id=message_id, body=body).execute()
    return {"id": result["id"], "labels": result.get("labelIds", [])}
