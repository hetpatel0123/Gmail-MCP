#!/usr/bin/env python3
"""CLI for managing Gmail MCP accounts."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import db, auth

def main():
    if len(sys.argv) < 2:
        print("Usage:\n  python cli.py list\n  python cli.py add EMAIL\n  python cli.py remove EMAIL")
        return
    command = sys.argv[1]
    if command == "list":
        accounts = db.list_accounts()
        if accounts:
            print("Authenticated accounts:")
            for acc in accounts: print(f"  - {acc}")
        else:
            print("No accounts authenticated.")
    elif command == "add":
        if len(sys.argv) < 3:
            print("Error: Please specify an email address")
            return
        email = sys.argv[2]
        print(f"Authenticating {email}... A browser window will open.")
        try:
            auth.authenticate_account(email)
            print(f"Successfully authenticated {email}")
        except Exception as e:
            print(f"Authentication failed: {e}")
    elif command == "remove":
        if len(sys.argv) < 3:
            print("Error: Please specify an email address")
            return
        email = sys.argv[2]
        print(f"Removed {email}" if db.remove_account(email) else f"Account {email} not found")
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
    