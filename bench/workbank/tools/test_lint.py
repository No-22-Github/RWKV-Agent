#!/usr/bin/env python3
"""test_lint.py — regression tests for lint.py forbidden-word checks.

Covers the nt-0001 slip: a notool case declaring no traps still must not
carry TR-NOTOOLNEED forbidden phrases, and phrase matching must tolerate
intervening words ("Without using any tools" matches "without tools").

Run from bench/workbank:  uv run python tools/test_lint.py
Stdlib only.
"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import lint  # noqa: E402

VOCAB = lint.DEFAULT_VOCAB
CONTRACT = json.loads(VOCAB.read_text(encoding="utf-8"))["answer_contracts"]["unknown"]

PROMPT_BODY = (
    "A monitoring dashboard reports an ingest rate of 2.5 MiB per second. "
    "Express that same rate in MiB per hour. "
)

NOTES = """## Traps
- None.
## Reference solution
No steps; ref_calls is 0.
## Why the answer is unique
The prompt supplies every input.
"""

VERIFY = """import json
case = json.load(open("case.json"))
print(json.dumps({"expected_number": 9000.0}))
"""


def make_case(root, prompt_body):
    case_dir = Path(root) / "notool" / "nt-9001"
    case_dir.mkdir(parents=True)
    case = {
        "id": "nt-9001",
        "description": "Convert a steady throughput; zero tool calls. WORKBANK-CANARY-0123abcd",
        "category": "notool",
        "tags": {
            "scenario": "notool",
            "task_type": "unit_convert",
            "traps": [],
            "trap_decoys": {},
            "axes": ["DEC"],
            "level": "L0",
            "ref_calls": 0,
            "fixture_bytes": 0,
            "status": "draft",
            "version": 1,
            "author": "llm:test",
            "reviewer": "human:test",
        },
        "files": {},
        "web_fixture": [],
        "turns": [
            {
                "prompt": prompt_body + CONTRACT,
                "expect": {"expected_number": 9000.0, "tolerance": 0.01, "tools": []},
            }
        ],
    }
    (case_dir / "case.json").write_text(
        json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (case_dir / "NOTES.md").write_text(NOTES, encoding="utf-8")
    (case_dir / "verify.py").write_text(VERIFY, encoding="utf-8")
    return case_dir


def run_lint(case_dir):
    out = io.StringIO()
    with redirect_stdout(out), redirect_stderr(io.StringIO()):
        code = lint.main(["--case", str(case_dir), "--vocab", str(VOCAB)])
    violations = [json.loads(line) for line in out.getvalue().splitlines() if line.strip()]
    return code, violations


class ForbiddenWordTest(unittest.TestCase):
    def lint_body(self, body):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = make_case(tmp, body)
            return run_lint(case_dir)

    def test_intervening_words_match_scenario_intrinsic_trap(self):
        # "Without using any tools" must trip TR-NOTOOLNEED's "without tools"
        # even though the case declares no traps (notool is intrinsic).
        code, violations = self.lint_body(
            "A dashboard shows 2.5 MiB per second. Without using any tools, "
            "express that rate in MiB per hour. ")
        self.assertEqual(code, 1)
        self.assertTrue(any(
            v["rule"] == "prompt.forbidden_word" and v["detail"].find("without tools") >= 0
            for v in violations), violations)

    def test_clean_prompt_passes(self):
        code, violations = self.lint_body(PROMPT_BODY)
        self.assertEqual(violations, [])
        self.assertEqual(code, 0)

    def test_tool_name_in_prompt_fails(self):
        code, violations = self.lint_body(
            PROMPT_BODY + "Use read_file to confirm. ")
        self.assertEqual(code, 1)
        self.assertTrue(any(v["rule"] == "prompt.tool_name" for v in violations), violations)


if __name__ == "__main__":
    unittest.main()
