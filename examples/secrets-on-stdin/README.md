# Secrets on standard input

A secret on a command line is readable by every process on the box (`ps`,
`/proc/<pid>/cmdline`) and ends up in shell history; a secret in the environment is
inherited by children and visible in `/proc/<pid>/environ`. So lab tools take secrets on
**stdin** and never log them.

[`secrets_on_stdin.py`](secrets_on_stdin.py) shows both sides of the pattern:

- `read_secret()` — how a tool *receives* a secret: it reads one line from stdin, and
  treats a secret found in argv or the environment as a loud misconfiguration error rather
  than a silent fallback.
- `run_with_secret()` — how a caller *supplies* a secret to a child: it writes the secret
  to the child's stdin, so it never appears in the child's argv or environment.
- `_redact()` — a reminder that a secret is masked before anything is logged.

## Run the tests

```bash
python3 test_secrets_on_stdin.py
```
