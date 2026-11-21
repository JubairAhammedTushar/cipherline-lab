# systemd hardening

Long-running lab services run as confined `systemd` units, so a bug or a compromise has as
little reach as possible. [`lab-service.service`](lab-service.service) is an annotated
reference unit that:

- runs as an unprivileged `DynamicUser` with `NoNewPrivileges` and an empty
  `CapabilityBoundingSet`;
- sees a read-only system (`ProtectSystem=strict`, `ProtectHome`), a private `/tmp`, and
  exactly one writable state directory;
- is kept away from the kernel, devices, clock and cgroups;
- is pinned to a `@system-service` syscall allow-list with `MemoryDenyWriteExecute`;
- defaults to local-only networking (`IPAddressDeny=any` + an allow-list) that you widen
  only if the service needs it.

Check any unit's exposure with:

```bash
systemd-analyze security lab-service.service
```

Then tighten each directive to what the service actually requires and re-run the analyzer —
the goal is a low score with the service still working, not copying this file as-is.
