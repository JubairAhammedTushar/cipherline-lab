# Forced-command SSH

The console reaches each lab machine over SSH, but it must never get a shell — only a
fixed set of jobs. SSH supports this directly: a key in `authorized_keys` can be pinned to
a single `command=`, and the client's real request arrives in `$SSH_ORIGINAL_COMMAND` for
the wrapper to accept or reject.

```
command="/usr/local/bin/forced-command.sh",no-pty,no-agent-forwarding,\
no-port-forwarding,no-X11-forwarding ssh-ed25519 AAAA... console@lab
```

[`forced-command.sh`](forced-command.sh) is a reference wrapper. It:

- reads the request as **words**, never evaluating it as a shell line;
- allows only a named list of jobs (`ping`, `vm-status`, `vm-start`, `backup`);
- validates each argument (a VM id is one to four digits, nothing else);
- runs the real tool with an **argument vector** (`exec qm status "$arg"`), so the id is
  data and can't smuggle in extra commands;
- logs and refuses everything else.

So `ssh lab "vm-status 101; rm -rf /"` is refused — the `;` is just more words that fail
validation, not a second command.

## Run the tests

```bash
bash test-forced-command.sh
```

The tests stub `qm`/`vzdump` on `PATH`, then check that allowed jobs call the right tool
and that unknown jobs, shell metacharacters, bad ids and extra arguments are all refused.
