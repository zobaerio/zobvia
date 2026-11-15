#!/usr/bin/env python3
"""Zobvia access gate.

Zobvia asks for an access password once per machine — at install time
(`install.sh` calls this) or the first time Claude uses the skill on a
new machine. Only a SHA-256 hash of the password lives in this file;
the password itself is never stored anywhere. On success a small marker
is written to ~/.zobvia/access-ok so the user is not asked again.

The access password is the author's GitHub username. This is a soft,
branding-level gate (the username is public), not cryptographic access
control — it exists so installing Zobvia is a deliberate act tied to
its author, exactly as the author requested.

Usage:
    python3 scripts/access_check.py            # check marker, else prompt
    python3 scripts/access_check.py --status   # 0 = unlocked, 3 = locked
    ZOBVIA_PASSWORD=... python3 scripts/access_check.py

Exit codes: 0 unlocked/verified, 2 wrong password, 3 locked (no input).
"""
from __future__ import annotations

import getpass
import hashlib
import hmac
import os
import sys
from pathlib import Path

# sha256 of the access password (the author's GitHub username, stripped).
EXPECTED_SHA256 = "cf0910915f3943f6a17e7aab4271bce12afc303505ecc795b17a1bc8020def52"

MARKER_DIR = Path.home() / ".zobvia"
MARKER_FILE = MARKER_DIR / "access-ok"


def password_matches(password: str) -> bool:
    """True iff the given password matches the stored hash."""
    digest = hashlib.sha256(password.strip().encode("utf-8")).hexdigest()
    return hmac.compare_digest(digest, EXPECTED_SHA256)


def is_unlocked() -> bool:
    """True iff a valid unlock marker exists on this machine."""
    try:
        return MARKER_FILE.read_text(encoding="utf-8").strip() == EXPECTED_SHA256
    except OSError:
        return False


def mark_unlocked() -> None:
    MARKER_DIR.mkdir(parents=True, exist_ok=True)
    MARKER_FILE.write_text(EXPECTED_SHA256 + "\n", encoding="utf-8")


def verify(password: str) -> bool:
    """Verify a password; on success, write the unlock marker."""
    if password_matches(password):
        mark_unlocked()
        return True
    return False


def main(argv: list[str]) -> int:
    if "--status" in argv:
        if is_unlocked():
            print("Zobvia: unlocked on this machine.")
            return 0
        print("Zobvia: locked — access password required.")
        return 3

    if is_unlocked():
        print("Zobvia: already unlocked on this machine.")
        return 0

    password = os.environ.get("ZOBVIA_PASSWORD", "")
    if not password:
        if not sys.stdin.isatty():
            print("Zobvia: locked — run install.sh or set ZOBVIA_PASSWORD.")
            return 3
        password = getpass.getpass("Zobvia access password: ")

    if verify(password):
        print("✅ Zobvia unlocked. Welcome!")
        return 0
    print("❌ Wrong access password. Hint: it is the author's GitHub username.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
