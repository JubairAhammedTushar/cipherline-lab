#!/usr/bin/env python3
"""Passing secrets on standard input (reference implementation).

A secret on the command line is visible to every other process (`ps`, `/proc/<pid>/cmdline`)
and lands in shell history; a secret in the environment is inherited by children and shows
up in `/proc/<pid>/environ`. So in the lab, tools receive secrets on **stdin** instead, and
never log them.

This module shows the pattern both ways round:

* ``read_secret()`` — how a tool *receives* a secret, from stdin, with argv/env as a
  loud misconfiguration error rather than a silent fallback.
* ``run_with_secret()`` — how a caller *supplies* a secret to a child process by writing
  it to the child's stdin, so it never appears in the child's argv or environment.

Run ``python3 secrets_on_stdin.py`` for a short self-check, or
``python3 test_secrets_on_stdin.py`` for the full tests.
"""
from __future__ import annotations

import subprocess
import sys


class MisconfiguredSecret(RuntimeError):
    """Raised when a secret arrives somewhere it should never be."""


def read_secret(argv: list[str] | None = None, environ: dict | None = None,
                stdin=None) -> str:
    """Return a single secret read from *stdin*.

    Refuses to run if a secret-looking value was passed on the command line or in the
    environment, so a misconfiguration fails loudly instead of leaking quietly.
    """
    argv = sys.argv if argv is None else argv
    environ = __import__("os").environ if environ is None else environ
    stdin = sys.stdin if stdin is None else stdin

    for token in argv[1:]:
        if token.startswith("--secret=") or token.startswith("--password="):
            raise MisconfiguredSecret("secret passed on the command line; use stdin")
    for key in ("SECRET", "PASSWORD", "TOKEN", "API_KEY"):
        if environ.get(key):
            raise MisconfiguredSecret(f"secret passed in ${key}; use stdin")

    secret = stdin.readline().rstrip("\n")
    if not secret:
        raise MisconfiguredSecret("no secret on stdin")
    return secret


def run_with_secret(cmd: list[str], secret: str) -> subprocess.CompletedProcess:
    """Run *cmd*, delivering *secret* on the child's stdin.

    The secret is never part of ``cmd`` (so it can't reach the child's argv) and the
    child inherits no secret environment variable from here.
    """
    return subprocess.run(
        cmd,
        input=secret + "\n",
        text=True,
        capture_output=True,
        check=True,
    )


def _redact(text: str, secret: str) -> str:
    """Never log a secret: replace it with a fixed marker before any logging."""
    return text.replace(secret, "***") if secret else text


if __name__ == "__main__":
    # Self-check: hand a secret to a child that reads stdin, prove it isn't in argv.
    demo = "correct horse battery staple"
    result = run_with_secret([sys.executable, "-c",
                              "import sys; print('child read', len(sys.stdin.readline().strip()), 'chars')"],
                             demo)
    print(result.stdout.strip())
    print("logged safely:", _redact(f"used secret {demo}", demo))
