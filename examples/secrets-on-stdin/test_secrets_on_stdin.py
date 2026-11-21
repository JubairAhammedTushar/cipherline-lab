#!/usr/bin/env python3
"""Tests for the secrets-on-stdin reference implementation."""
import io
import sys
import unittest

import secrets_on_stdin as s


class ReadSecret(unittest.TestCase):
    def test_reads_from_stdin(self):
        got = s.read_secret(argv=["tool"], environ={}, stdin=io.StringIO("hunter2\n"))
        self.assertEqual(got, "hunter2")

    def test_rejects_command_line_secret(self):
        with self.assertRaises(s.MisconfiguredSecret):
            s.read_secret(argv=["tool", "--secret=hunter2"], environ={},
                          stdin=io.StringIO("hunter2\n"))

    def test_rejects_environment_secret(self):
        with self.assertRaises(s.MisconfiguredSecret):
            s.read_secret(argv=["tool"], environ={"PASSWORD": "hunter2"},
                          stdin=io.StringIO("hunter2\n"))

    def test_empty_stdin_is_an_error(self):
        with self.assertRaises(s.MisconfiguredSecret):
            s.read_secret(argv=["tool"], environ={}, stdin=io.StringIO(""))


class RunWithSecret(unittest.TestCase):
    def test_child_gets_secret_on_stdin_not_argv(self):
        secret = "s3cr3t-value"
        # The child prints its own argv and whatever it read on stdin.
        code = ("import sys;"
                "print('ARGV', sys.argv[1:]);"
                "print('STDIN', sys.stdin.readline().strip())")
        r = s.run_with_secret([sys.executable, "-c", code], secret)
        self.assertIn(f"STDIN {secret}", r.stdout)
        self.assertNotIn(secret, r.stdout.split("STDIN")[0])  # not in the ARGV line


class Redact(unittest.TestCase):
    def test_secret_is_redacted_before_logging(self):
        self.assertEqual(s._redact("token=abc123 ok", "abc123"), "token=*** ok")


if __name__ == "__main__":
    unittest.main()
