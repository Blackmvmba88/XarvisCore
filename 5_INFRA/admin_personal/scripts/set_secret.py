#!/usr/bin/env python3
"""scripts/set_secret.py
Set a secret into Keyring via `services.secret_store.set_secret`.
Usage:
  python scripts/set_secret.py --service SERVICE --username USERNAME [--secret SECRET] [--encrypt]
If --secret is omitted you'll be prompted to type it securely.
"""
import argparse
import getpass
from services import secret_store

parser = argparse.ArgumentParser()
parser.add_argument("--service", required=True)
parser.add_argument("--username", required=True)
parser.add_argument("--secret", help="Secret value (avoid providing on CLI if possible)")
parser.add_argument("--encrypt", action="store_true", help="Store encrypted with Fernet (requires cryptography)")
args = parser.parse_args()

secret = args.secret
if not secret:
    secret = getpass.getpass("Secret: ")

secret_store.set_secret(args.service, args.username, secret, encrypt=args.encrypt)
print(f"Stored secret for {args.service}/{args.username} (encrypt={args.encrypt})")
