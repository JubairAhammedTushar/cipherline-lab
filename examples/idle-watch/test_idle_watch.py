#!/usr/bin/env python3
"""Tests for the idle-watch reference implementation."""
import unittest

from idle_watch import IdleWatch


class IsBusy(unittest.TestCase):
    def test_busy_when_any_device_is_active(self):
        w = IdleWatch(busy_kbit_per_device=20.0)
        self.assertTrue(w.is_busy({"a": 1.0, "b": 500.0}))

    def test_idle_when_all_below_threshold(self):
        w = IdleWatch(busy_kbit_per_device=20.0)
        self.assertFalse(w.is_busy({"a": 1.0, "b": 19.9}))

    def test_no_devices_is_not_busy(self):
        self.assertFalse(IdleWatch().is_busy({}))


class Update(unittest.TestCase):
    def test_becomes_ready_after_enough_quiet_checks(self):
        w = IdleWatch(busy_kbit_per_device=20.0, quiet_checks_needed=3)
        self.assertFalse(w.update({"a": 1.0}))   # quiet 1
        self.assertFalse(w.update({"a": 1.0}))   # quiet 2
        self.assertTrue(w.update({"a": 1.0}))    # quiet 3 -> ready

    def test_activity_resets_the_quiet_run(self):
        w = IdleWatch(busy_kbit_per_device=20.0, quiet_checks_needed=3)
        w.update({"a": 1.0})                      # quiet 1
        w.update({"a": 1.0})                      # quiet 2
        self.assertFalse(w.update({"a": 999.0}))  # busy -> reset
        self.assertFalse(w.update({"a": 1.0}))    # quiet 1 again
        self.assertFalse(w.update({"a": 1.0}))    # quiet 2
        self.assertTrue(w.update({"a": 1.0}))     # quiet 3 -> ready

    def test_reset_clears_progress(self):
        w = IdleWatch(quiet_checks_needed=2)
        w.update({"a": 0.0})
        w.reset()
        self.assertFalse(w.ready)


if __name__ == "__main__":
    unittest.main()
