"""Tests for the command-line interface."""

import contextlib
import io
import json
import os
import tempfile
import unittest

from agent_market_signals.__main__ import main


def _write(payload) -> str:
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)
    return path


class CliTests(unittest.TestCase):
    def _run(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_clean_board_exits_zero(self):
        path = _write([{"id": "a", "created_at": "2026-07-12T00:00:00Z"}])
        try:
            code, out, _ = self._run([path])
        finally:
            os.unlink(path)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["verdict"], "clear")

    def test_high_finding_exits_one(self):
        path = _write(
            [
                {
                    "id": "bait",
                    "created_at": "2026-07-12T00:00:00Z",
                    "views": 0,
                    "applications": 24,
                },
                {
                    "id": "normal",
                    "created_at": "2026-07-11T00:00:00Z",
                    "views": 10,
                    "applications": 2,
                },
            ]
        )
        try:
            code, out, _ = self._run([path])
        finally:
            os.unlink(path)
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["verdict"], "high_risk")

    def test_missing_file_is_clean_error_not_traceback(self):
        code, _, err = self._run(["/nonexistent/listings.json"])
        self.assertEqual(code, 2)
        self.assertIn("error:", err)

    def test_bad_json_is_clean_error(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as fh:
            fh.write("{not json")
        try:
            code, _, err = self._run([path])
        finally:
            os.unlink(path)
        self.assertEqual(code, 2)
        self.assertIn("error:", err)

    def test_non_array_input_is_clean_error(self):
        path = _write({"id": "x"})
        try:
            code, _, err = self._run([path])
        finally:
            os.unlink(path)
        self.assertEqual(code, 2)
        self.assertIn("array", err)

    def test_help_exits_zero(self):
        with self.assertRaises(SystemExit) as ctx:
            self._run(["--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
