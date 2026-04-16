#!/usr/bin/env python3
"""scripts/assistant_cli.py
Simple CLI to call the local /assistant/message endpoint using the admin API key stored in Keyring.
"""
import requests
import sys
from services import secret_store

API_URL = "http://127.0.0.1:8000/assistant/message"

def main():
    if len(sys.argv) < 2:
        print("Usage: assistant_cli.py 'your message here'")
        sys.exit(1)
    message = sys.argv[1]
    key = secret_store.get_secret("app", "admin_api_key")
    if not key:
        print("No admin API key found in Keyring. Set it with scripts/set_api_key.py --admin <key>")
        sys.exit(1)
    resp = requests.post(API_URL, json={"message": message, "dry_run": True}, headers={"X-API-KEY": key})
    print(resp.json())

if __name__ == "__main__":
    main()
