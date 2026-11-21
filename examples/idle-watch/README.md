# Idle-aware batch work

Updates, reboots and backups shouldn't interrupt someone mid-call. The gateway publishes a
small **activity meter** — per-device throughput over the last interval — and batch jobs
read it before acting.

[`idle_watch.py`](idle_watch.py) is the decision logic on its own, with no I/O:

- `is_busy(samples)` — is any device above the activity threshold right now?
- `update(samples)` — record one sample; returns `True` once the link has been quiet for
  several consecutive checks. **Any** activity during the wait resets the count, so one
  busy sample restarts it.

Keeping this as pure logic means it's fully testable without a network.

## Run the tests

```bash
python3 test_idle_watch.py
```
