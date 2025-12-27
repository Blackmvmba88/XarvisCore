#!/usr/bin/env python3
"""scripts/set_api_key.py
Helper to set admin API key for the app and optionally the OpenAI API key in Keyring.
Usage: python scripts/set_api_key.py --admin <ADMIN_KEY> [--openai <OPENAI_KEY>]
"""
import argparse
from services import secret_store

parser = argparse.ArgumentParser()
parser.add_argument("--admin", help="API key for app (required to use endpoints)")
parser.add_argument("--openai", help="OpenAI API key to store in Keyring (optional)")
args = parser.parse_args()

if args.admin:
    secret_store.set_secret("app", "admin_api_key", args.admin, encrypt=False)
    print("Stored admin API key in Keyring (service='app', username='admin_api_key')")

if args.openai:
    secret_store.set_secret("openai", "api_key", args.openai, encrypt=False)
    print("Stored OpenAI API key in Keyring (service='openai', username='api_key')")

if not args.admin and not args.openai:
    parser.print_help()
