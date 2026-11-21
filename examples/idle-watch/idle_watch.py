#!/usr/bin/env python3
"""Activity-aware idle detection (reference implementation).

Maintenance in the lab — updates, reboots, backups — must not land while someone is in a
video call. The gateway publishes a small **activity meter**: for each connected device,
the throughput over the last interval. A batch job doesn't act until the link has been
quiet for several consecutive checks.

This module is the decision logic on its own, with no I/O: feed it throughput samples and
it tells you whether the link is "busy" now and whether it has been quiet long enough to
proceed. The thresholds here are illustrative, not the live lab's values.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class IdleWatch:
    """Decide when a link is quiet enough for batch work.

    :param busy_kbit_per_device: a device is "active" above this throughput
    :param quiet_checks_needed: how many consecutive quiet samples before "idle"
    """
    busy_kbit_per_device: float = 20.0
    quiet_checks_needed: int = 5
    _quiet_run: int = field(default=0, init=False)

    def is_busy(self, per_device_kbit: dict[str, float]) -> bool:
        """True if any device is above the activity threshold right now."""
        return any(rate >= self.busy_kbit_per_device
                   for rate in per_device_kbit.values())

    def update(self, per_device_kbit: dict[str, float]) -> bool:
        """Record one sample; return True once the link has been quiet long enough.

        Any activity resets the quiet run to zero, so a single busy sample during the
        wait restarts the count.
        """
        if self.is_busy(per_device_kbit):
            self._quiet_run = 0
        else:
            self._quiet_run += 1
        return self.ready

    @property
    def ready(self) -> bool:
        return self._quiet_run >= self.quiet_checks_needed

    def reset(self) -> None:
        self._quiet_run = 0


if __name__ == "__main__":
    # A device streams, then goes quiet; the job waits, then proceeds.
    w = IdleWatch(busy_kbit_per_device=20.0, quiet_checks_needed=3)
    samples = [
        {"phone": 5.0, "laptop": 1800.0},   # someone is streaming
        {"phone": 4.0, "laptop": 12.0},     # quiet 1
        {"phone": 0.0, "laptop": 9.0},      # quiet 2
        {"phone": 2.0, "laptop": 3.0},      # quiet 3  -> ready
    ]
    for i, s in enumerate(samples, 1):
        ready = w.update(s)
        print(f"check {i}: busy={w.is_busy(s)} ready={ready}")
