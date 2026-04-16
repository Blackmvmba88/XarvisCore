#!/usr/bin/env python3
"""scripts/vault.py
Small vault CLI to manage secrets using the project's `services.secret_store`.
Supports add/get/list/delete/export/import (optional GPG encryption for export/import).

Usage examples:
  python scripts/vault.py add --service mysite --username me --encrypt
  python scripts/vault.py get --service mysite --username me --show
  python scripts/vault.py list
  python scripts/vault.py delete --service mysite --username me
  python scripts/vault.py export --out backup.json
  python scripts/vault.py export --out backup.json --gpg
  python scripts/vault.py import --in backup.json
  python scripts/vault.py import --in backup.json.gpg

Security notes:
- This uses Keyring to store values (Keychain on macOS). Use `--encrypt` to store encrypted blobs with Fernet (requires `cryptography`).
- Do NOT paste secrets into chats. Prefer typing or using stdin.
"""

import argparse
import getpass
import json
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Optional

from services import secret_store


def cmd_add(args):
    secret = args.secret
    if not secret:
        secret = getpass.getpass("Secret: ")
    secret_store.set_secret(args.service, args.username, secret, encrypt=args.encrypt)
    print(f"Stored secret for {args.service}/{args.username} (encrypt={args.encrypt})")


def cmd_get(args):
    val = secret_store.get_secret(args.service, args.username, decrypt=args.decrypt)
    if val is None:
        print("Not found")
        return
    if args.show:
        print(val)
    else:
        # show masked
        print("Value hidden. Use --show to display the secret (careful!).")


def cmd_list(args):
    idx = secret_store.list_secrets()
    if not idx:
        print("No secrets stored")
        return
    for service, users in idx.items():
        print(f"{service}:")
        for u in users:
            print(f"  - {u}")


def cmd_delete(args):
    secret_store.delete_secret(args.service, args.username)
    print(f"Deleted {args.service}/{args.username} (if existed)")


def _write_temp_json(data) -> str:
    fd, path = tempfile.mkstemp(prefix="vault_export_", suffix=".json")
    os.close(fd)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path


def cmd_export(args):
    idx = secret_store.list_secrets()
    out = {"items": []}
    for service, users in idx.items():
        for u in users:
            val = secret_store.get_secret(service, u, decrypt=args.decrypt)
            out["items"].append({"service": service, "username": u, "secret": val, "encrypted": False})

    if args.out is None:
        print(json.dumps(out, indent=2))
        return

    if args.gpg:
        tmp = _write_temp_json(out)
        try:
            subprocess.run(["gpg", "--symmetric", "--cipher-algo", "AES256", "-o", args.out, tmp], check=True)
            print(f"Exported and encrypted to {args.out} (symmetric GPG)")
        finally:
            try:
                os.remove(tmp)
            except Exception:
                pass
    else:
        with open(args.out, "w") as f:
            json.dump(out, f, indent=2)
        print(f"Exported JSON to {args.out}")


def cmd_import(args):
    inp = args.infile
    # If file ends with .gpg or --gpg flag, try decrypting via gpg
    is_gpg = inp.endswith(".gpg") or args.gpg
    if is_gpg:
        fd, tmp = tempfile.mkstemp(prefix="vault_import_", suffix=".json")
        os.close(fd)
        try:
            subprocess.run(["gpg", "--decrypt", "-o", tmp, inp], check=True)
            with open(tmp) as f:
                data = json.load(f)
        finally:
            try:
                os.remove(tmp)
            except Exception:
                pass
    else:
        with open(inp) as f:
            data = json.load(f)

    items = data.get("items", [])
    for it in items:
        svc = it.get("service")
        usr = it.get("username")
        sec = it.get("secret")
        if svc and usr and sec is not None:
            secret_store.set_secret(svc, usr, sec, encrypt=False)
            print(f"Imported {svc}/{usr}")


def main():
    parser = argparse.ArgumentParser(prog="vault")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("add")
    p.add_argument("--service", required=True)
    p.add_argument("--username", required=True)
    p.add_argument("--secret")
    p.add_argument("--encrypt", action="store_true")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("get")
    p.add_argument("--service", required=True)
    p.add_argument("--username", required=True)
    p.add_argument("--show", action="store_true", help="Show the secret value (dangerous)")
    p.add_argument("--decrypt", action="store_true", help="Attempt Fernet decrypt if available")
    p.set_defaults(func=cmd_get)

    p = sub.add_parser("list")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("delete")
    p.add_argument("--service", required=True)
    p.add_argument("--username", required=True)
    p.set_defaults(func=cmd_delete)

    p = sub.add_parser("export")
    p.add_argument("--out", help="Output file (JSON) ; if omitted prints to stdout")
    p.add_argument("--gpg", action="store_true", help="Encrypt output with gpg symmetric")
    p.add_argument("--decrypt", action="store_true", help="Attempt to decrypt stored values before export")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("import")
    p.add_argument("--in", dest="infile", required=True, help="Input file (JSON or .gpg)")
    p.add_argument("--gpg", action="store_true", help="Treat input as gpg-encrypted")
    p.set_defaults(func=cmd_import)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
