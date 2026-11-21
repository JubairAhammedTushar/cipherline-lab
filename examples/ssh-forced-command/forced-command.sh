#!/usr/bin/env bash
# Forced-command wrapper (reference implementation)
# ------------------------------------------------
# One SSH key, a fixed allow-list of jobs, validated arguments, never a shell.
#
# In authorized_keys the key is pinned to this script:
#
#   command="/usr/local/bin/forced-command.sh",no-pty,no-agent-forwarding,\
#   no-port-forwarding,no-X11-forwarding ssh-ed25519 AAAA... console@lab
#
# The client asks for a job by name, e.g.  ssh lab vm-status 101
# The real request arrives in $SSH_ORIGINAL_COMMAND; the key can do nothing else.
#
# This is a generic illustration of the pattern, not the live lab's command set.
set -euo pipefail
umask 077

log() { logger -t forced-command -- "$*" 2>/dev/null || true; }
deny() { log "DENY: ${SSH_ORIGINAL_COMMAND:-<none>} ($1)"; echo "not allowed" >&2; exit 1; }

# Split the requested command into a verb and at most one argument. No shell is
# ever invoked on the client's string: we read words, we do not evaluate them.
read -r -a REQ <<<"${SSH_ORIGINAL_COMMAND:-}"
verb="${REQ[0]:-}"
arg="${REQ[1]:-}"
[ "${#REQ[@]}" -le 2 ] || deny "too many arguments"

# A VM id is one to four digits and nothing else.
valid_vmid() { [[ "$1" =~ ^[0-9]{1,4}$ ]]; }

case "$verb" in
  ping)
    [ -z "$arg" ] || deny "ping takes no argument"
    echo "pong"
    ;;
  vm-status)
    valid_vmid "$arg" || deny "bad vm id"
    # exec with an argument vector — the id is data, never part of a command line
    exec qm status "$arg"
    ;;
  vm-start)
    valid_vmid "$arg" || deny "bad vm id"
    exec qm start "$arg"
    ;;
  backup)
    valid_vmid "$arg" || deny "bad vm id"
    exec vzdump "$arg" --mode snapshot --quiet 1
    ;;
  *)
    deny "unknown job"
    ;;
esac
