"""OAuth2 authentication for Gmail API."""
import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

from db import save_tokens, get_tokens

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels",
]
PROJECT_ROOT = Path(__file__).resolve().parent
ENV_FILE = PROJECT_ROOT / ".env"
OAUTH_CREDENTIALS = Path.home() / ".gmail-mcp-oauth.json"


def _load_environment():
    # Prefer credentials from project-local .env while still allowing shell vars.
    load_dotenv(ENV_FILE)
    load_dotenv()


_load_environment()


def get_oauth_config():
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

    if client_id and client_secret:
        return {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"]
            }
        }

    if client_id or client_secret:
        raise ValueError(
            "Incomplete Google OAuth configuration. Set both GOOGLE_CLIENT_ID and "
            "GOOGLE_CLIENT_SECRET together."
        )

    if OAUTH_CREDENTIALS.exists():
        return json.loads(OAUTH_CREDENTIALS.read_text())

    raise ValueError(
        "No OAuth credentials found. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET "
        f"in {ENV_FILE} or create {OAUTH_CREDENTIALS}"
    )

def authenticate_account(email):
    config = get_oauth_config()
    flow = InstalledAppFlow.from_client_config(config, SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent",
        authorization_prompt_message=f"Please sign in with: {email}")
    save_tokens(email, creds.token, creds.refresh_token, creds.expiry,
        list(creds.scopes) if creds.scopes else SCOPES)
    return creds

def get_credentials(email):
    tokens = get_tokens(email)
    if not tokens:
        return None
    config = get_oauth_config()
    creds = Credentials(
        token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=config["installed"]["client_id"],
        client_secret=config["installed"]["client_secret"],
        scopes=tokens["scopes"] or SCOPES
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        save_tokens(email, creds.token, creds.refresh_token, creds.expiry,
            list(creds.scopes) if creds.scopes else SCOPES)
    return creds
