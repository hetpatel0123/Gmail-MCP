# Gmail MCP Server

Multi-account Gmail MCP server with OAuth authentication and Gmail tools.

## Quick Start

1. Install dependencies:
```bash
uv sync
```

2. Create local environment file:
```bash
cp .env.example .env
```
On Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

3. Put your Google OAuth credentials in `.env`:
```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

4. Run the server:
```bash
uv run gmail-mcp
```

No need to run `$env:GOOGLE_CLIENT_ID=...` every time. The server auto-loads `.env`.

## First-Time Account Setup

Authenticate one or more Gmail accounts:
```bash
uv run gmail-mcp-cli add your-email@gmail.com
```

List accounts:
```bash
uv run gmail-mcp-cli list
```

Remove an account:
```bash
uv run gmail-mcp-cli remove your-email@gmail.com
```

## MCP Tools Included

- `list_accounts`
- `add_account`
- `remove_account`
- `search_emails`
- `read_email`
- `send_email`
- `get_labels`
- `archive_email`
- `mark_as_read`
- `mark_as_unread`

## Notes

- Token DB is stored at: `~/.gmail-mcp-tokens.db`
- Optional OAuth JSON fallback path: `~/.gmail-mcp-oauth.json`
- For local OAuth browser flow, running directly on your machine is easier than Docker.
