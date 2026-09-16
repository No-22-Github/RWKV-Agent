#!/usr/bin/env python3
"""verify_all.py — run every case's verify.py and check it against the case expect.

For each case directory (a directory containing case.json + verify.py, found
recursively under --cases):

1. Materialize case.json's `files` into a temp copy of the case dir (case
   dirs carry fixtures inside case.json, not on disk), then run
   `python3 -I -S verify.py` with cwd=temp dir, a 10s timeout and an
   environment stripped down to PATH/HOME. stdout must parse as JSON.
   Recognised shapes:
     - {"expected_number": x}        compared against turns[].expect.expected_number
     - {"files": {path: content}}    compared against expect.files equals/contains
     - {"expected_string": s} / {"expected": s} — the string is tried against
       every output_equals (exact) and every expected_number (numeric, with
       tolerance). web-9001 in testdata uses this shape.
   Any other shape records a `verify_shape_unknown` warning, not a failure.
2. Sabotage test: materialize the case into a second temp dir with the
   fixture files corrupted (if an expected_number exists, increment the first
   number in the files that is numerically equal to it; otherwise delete the
   first non-empty line of a CSV/text file), re-run verify.py and assert the
   output no longer matches the original expectation. A verify.py that still
   matches after sabotage agrees with expect by construction (same-source
   bug) and is reported as `sabotage_undetected`.

Exit status is 1 if any case failed, 0 otherwise. Stdout is a JSON report.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VERIFY_TIMEOUT = 10.0
DEFAULT_TOLERANCE = 0.01
NUMBER_RE = re.compile(r"(?<![\w.])(-?\d+(?:\.\d+)?)(?![\w.])")
# Corruption prefers data files over prose: verify.py reads data, not READMEs.
EXT_ORDER = [".csv", ".tsv", ".txt", ".jsonl", ".log", ".json", ".yaml", ".yml", ".md"]


def find_case_dirs(root):
    root = Path(root)
    if (root / "case.json").is_file():
        return [root]
    if not root.is_dir():
        raise NotADirectoryError(str(root))
    dirs = [p.parent for p in root.rglob("case.json")]
    return sorted(dirs, key=lambda p: str(p))


def run_verify(case_dir):
    env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
    }
    try:
        proc = subprocess.run(
            ["python3", "-I", "-S", "verify.py"],
            cwd=str(case_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=VERIFY_TIMEOUT,
        )
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "error": None,
        }
    except subprocess.TimeoutExpired:
        return {"returncode": None, "stdout": "", "stderr": "", "error": "timeout after %ss" % VERIFY_TIMEOUT}
    except OSError as exc:
        return {"returncode": None, "stdout": "", "stderr": "", "error": str(exc)}


def parse_verify_stdout(stdout):
    """Parse the whole stdout as JSON, falling back to the last non-empty line."""
    text = (stdout or "").strip()
    if not text:
        return None, "empty stdout"
    try:
        return json.loads(text), None
    except json.JSONDecodeError:
        pass
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line), None
        except json.JSONDecodeError:
            continue
    return None, "stdout is not JSON"


def case_expectations(case):
    """Collect (expected_numbers, output_equals, expect.files) from a case."""
    numbers, output_equals = [], []
    for turn in case.get("turns") or []:
        if not isinstance(turn, dict):
            continue
        exp = turn.get("expect") or {}
        val = exp.get("expected_number")
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            tol = exp.get("tolerance")
            if not isinstance(tol, (int, float)) or isinstance(tol, bool) or tol <= 0:
                tol = DEFAULT_TOLERANCE
            numbers.append((float(val), float(tol)))
        oe = exp.get("output_equals")
        if isinstance(oe, str):
            output_equals.append(oe)
    file_exp = {}
    case_exp = case.get("expect") or {}
    if isinstance(case_exp.get("files"), dict):
        file_exp = case_exp["files"]
    return numbers, output_equals, file_exp


def _num_eq(a, b, tol):
    return abs(a - b) <= max(tol, 1e-12)


def matches_expectation(obj, numbers, output_equals, file_exp):
    """Try to match a parsed verify.py output against the case expect.

    Returns (matched, detail): matched is True/False, or None when the shape
    is not recognised (verify_shape_unknown).
    """
    if not isinstance(obj, dict):
        return None, "output is not a JSON object"
    exp_num = obj.get("expected_number")
    if exp_num is None:
        maybe = obj.get("expected")
        if isinstance(maybe, (int, float)) and not isinstance(maybe, bool):
            exp_num = maybe
    if exp_num is not None:
        try:
            val = float(exp_num)
        except (TypeError, ValueError):
            return False, "expected_number is not numeric: %r" % (exp_num,)
        if not numbers:
            return False, "verify outputs a number but no turn expect has expected_number"
        for v, tol in numbers:
            if _num_eq(val, v, tol):
                return True, "number %r matches expected_number %r (tol %s)" % (val, v, tol)
        return False, "number %r matches none of expected_number %s" % (
            val, [v for v, _ in numbers])

    if "files" in obj:
        files = obj.get("files")
        if not isinstance(files, dict):
            return False, "verify 'files' is not an object"
        problems, compared = [], False
        for path, exp in (file_exp or {}).items():
            if not isinstance(exp, dict):
                continue
            if "equals" in exp:
                compared = True
                if files.get(path) != exp["equals"]:
                    problems.append("%s: equals mismatch" % path)
            contains = exp.get("contains")
            if isinstance(contains, list):
                compared = True
                content = files.get(path)
                if not isinstance(content, str):
                    problems.append("%s: missing from verify output" % path)
                else:
                    for sub in contains:
                        if sub not in content:
                            problems.append("%s: missing substring %r" % (path, sub))
        if problems:
            return False, "; ".join(problems)
        if compared:
            return True, "files match expect.files"
        return True, "files output present; expect.files has no equals/contains to compare"

    sval = obj.get("expected_string")
    if sval is None and isinstance(obj.get("expected"), str):
        sval = obj["expected"]
    if isinstance(sval, str):
        if sval in output_equals:
            return True, "string %r matches output_equals" % sval
        for v, tol in numbers:
            try:
                fval = float(sval.strip())
            except ValueError:
                continue
            if _num_eq(fval, v, tol):
                return True, "string %r matches expected_number %r" % (sval, v)
        return False, "string %r matches neither output_equals %s nor expected_number %s" % (
            sval, output_equals, [v for v, _ in numbers])

    return None, "unrecognized verify output shape (keys: %s)" % sorted(obj)


def _ext_rank(name):
    lower = name.lower()
    for i, ext in enumerate(EXT_ORDER):
        if lower.endswith(ext):
            return i
    return len(EXT_ORDER)


def _corrupt_numeric(files, expected, tol):
    """Increment the first number (across files) numerically equal to expected."""
    for path in sorted(files, key=lambda p: (_ext_rank(Path(p).name), p)):
        content = files[path]
        if not isinstance(content, str) or not content:
            continue
        for m in NUMBER_RE.finditer(content):
            try:
                val = float(m.group(1))
            except ValueError:
                continue
            if abs(val - expected) > max(tol, 1e-9):
                continue
            orig = m.group(1)
            new = val + 1.0
            new_s = str(int(new)) if ("." not in orig and float(new).is_integer()) else repr(new)
            start, end = m.span(1)
            return path, content[:start] + new_s + content[end:], "%s -> %s" % (orig, new_s)
    return None


def _corrupt_first_line(files):
    """Delete the first non-empty line of the first CSV/text file that has one."""
    for path in sorted(files, key=lambda p: (_ext_rank(Path(p).name), p)):
        content = files[path]
        if not isinstance(content, str) or not content:
            continue
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.strip():
                del lines[i]
                return path, "\n".join(lines), "deleted first non-empty line"
    return None


def materialize_case_dir(case_dir, case, files_override=None):
    """Copy the case dir to a temp dir and write case.json's `files` to disk.

    Case fixtures live inside case.json (schema v5); verify.py reads them from
    its working directory. files_override replaces the content of specific
    paths (used by the sabotage test). Caller removes the returned dir.
    """
    tmp = Path(tempfile.mkdtemp(prefix="verify_all_")) / Path(case_dir).name
    shutil.copytree(case_dir, tmp,
                    ignore=shutil.ignore_patterns("__pycache__", ".venv"))
    files = case.get("files") or {}
    override = files_override or {}
    for rel, content in files.items():
        if rel in override:
            content = override[rel]
        target = tmp / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content if isinstance(content, str) else str(content),
                          encoding="utf-8")
    if override:
        # The bank contract (HANDOFF section 2.2) lets verify.py read fixtures
        # either from case.json or from its working directory. The sabotage
        # must be visible to both styles, so rewrite the copied case.json too.
        case_copy = tmp / "case.json"
        if case_copy.is_file():
            embedded = json.loads(case_copy.read_text(encoding="utf-8"))
            embedded_files = embedded.get("files") or {}
            for rel, content in override.items():
                embedded_files[rel] = content
            embedded["files"] = embedded_files
            case_copy.write_text(json.dumps(embedded, ensure_ascii=False),
                                 encoding="utf-8")
    return tmp


def sabotage_and_rerun(case_dir, case, numbers, output_equals, file_exp):
    files = case.get("files") or {}
    if not files:
        return {"check": "sabotage", "ok": True,
                "warning": "sabotage_skipped_no_files",
                "detail": "case has no files to corrupt"}
    if numbers:
        expected, tol = numbers[0]
        plan = _corrupt_numeric(files, expected, tol)
        method = "number+1"
    else:
        plan, method = None, None
    if plan is None:
        plan = _corrupt_first_line(files)
        method = "delete_first_line"
    if plan is None:
        return {"check": "sabotage", "ok": True,
                "warning": "sabotage_skipped_no_content",
                "detail": "no corruptable number or line found in case files"}
    path, new_content, note = plan
    tmp = materialize_case_dir(case_dir, case, files_override={path: new_content})
    try:
        res = run_verify(tmp)
    finally:
        shutil.rmtree(tmp.parent, ignore_errors=True)
    label = "%s on %s (%s)" % (method, path, note)
    if res["error"] or res["returncode"] != 0:
        return {"check": "sabotage", "ok": True,
                "detail": "%s; verify.py failed after sabotage (detected)" % label}
    obj, perr = parse_verify_stdout(res["stdout"])
    if obj is None:
        return {"check": "sabotage", "ok": True,
                "detail": "%s; verify output unparseable after sabotage (detected)" % label}
    matched, mdetail = matches_expectation(obj, numbers, output_equals, file_exp)
    if matched is True:
        return {"check": "sabotage", "ok": False, "error": "sabotage_undetected",
                "detail": "%s but verify.py still matches expect: %s" % (label, mdetail)}
    return {"check": "sabotage", "ok": True,
            "detail": "%s; output diverged: %s" % (label, mdetail)}


def verify_case(case_dir):
    case_dir = Path(case_dir)
    case_path = case_dir / "case.json"
    try:
        case = json.loads(case_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"case": str(case_dir), "ok": False,
                "checks": [{"check": "case_json", "ok": False, "error": "case.json missing"}]}
    except (OSError, json.JSONDecodeError) as exc:
        return {"case": str(case_dir), "ok": False,
                "checks": [{"check": "case_json", "ok": False, "error": "case.json unreadable: %s" % exc}]}
    case_id = case.get("id") or case_dir.name
    if not (case_dir / "verify.py").is_file():
        return {"case": case_id, "ok": False,
                "checks": [{"check": "verify_py", "ok": False, "error": "verify.py missing"}]}
    checks = []
    numbers, output_equals, file_exp = case_expectations(case)
    tmp = materialize_case_dir(case_dir, case)
    try:
        res = run_verify(tmp)
    finally:
        shutil.rmtree(tmp.parent, ignore_errors=True)
    if res["error"] or res["returncode"] != 0:
        err = res["error"] or "exit code %s" % res["returncode"]
        stderr_lines = [ln for ln in (res["stderr"] or "").strip().splitlines() if ln.strip()]
        checks.append({"check": "verify_run", "ok": False, "error": "verify.py failed: %s" % err,
                       "detail": stderr_lines[-1] if stderr_lines else None})
        return {"case": case_id, "ok": False, "checks": checks}
    obj, perr = parse_verify_stdout(res["stdout"])
    if obj is None:
        checks.append({"check": "verify_output", "ok": False,
                       "error": "verify.py stdout is not JSON: %s" % perr})
        return {"case": case_id, "ok": False, "checks": checks}
    # Offline-run cases: verify.py must independently derive the same stdout
    # the harness will compare the model script against. Without this the
    # expect side of expect.run was never cross-checked (audit W-finding).
    run_exp = (case.get("expect") or {}).get("run") or {}
    if run_exp.get("expected_stdout") is not None and "expected_stdout" in obj:
        same = obj.get("expected_stdout") == run_exp["expected_stdout"]
        checks.append({"check": "run_expect_match", "ok": same,
                       "detail": "verify.py expected_stdout %s expect.run.expected_stdout"
                                 % ("matches" if same else "DIFFERS from")})
        if not same:
            return {"case": case_id, "ok": False, "checks": checks}
    matched, mdetail = matches_expectation(obj, numbers, output_equals, file_exp)
    if matched is None:
        checks.append({"check": "verify_shape", "ok": True,
                       "warning": "verify_shape_unknown", "detail": mdetail})
    elif matched is True:
        checks.append({"check": "expect_match", "ok": True, "detail": mdetail})
    else:
        checks.append({"check": "expect_match", "ok": False,
                       "error": "verify_expect_mismatch", "detail": mdetail})
        return {"case": case_id, "ok": False, "checks": checks}
    checks.append(sabotage_and_rerun(case_dir, case, numbers, output_equals, file_exp))
    ok = all(c.get("ok", False) for c in checks)
    return {"case": case_id, "ok": ok, "checks": checks}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Run every case's verify.py against case.json expect, plus a sabotage test.",
        epilog="Output: JSON report on stdout; exit 1 if any case failed.")
    ap.add_argument("--cases", required=True,
                    help="case root directory (searched recursively for case.json), or a single case dir")
    args = ap.parse_args(argv)

    try:
        case_dirs = find_case_dirs(args.cases)
    except NotADirectoryError:
        print("error: --cases %s is not a directory" % args.cases, file=sys.stderr)
        return 2
    results = [verify_case(d) for d in case_dirs]
    failed = [r for r in results if not r["ok"]]
    report = {
        "cases_root": str(args.cases),
        "total": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "results": results,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    for r in results:
        status = "ok" if r["ok"] else "FAIL"
        print("%s %s" % (status, r["case"]), file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
