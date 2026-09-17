#!/usr/bin/env python3
"""ledger.py — append-only scoring ledger for workbank runs.

Subcommands:
  ingest  Read run.json + summary.json from a run directory and append one
          row per run to ledger/runs.jsonl and one row per run x case x k to
          ledger/cases.jsonl. Ingest is idempotent: a run row is skipped when
          (run_id, k_index) already exists; a case row is skipped when
          (run_id, case_id, k_index) already exists. Old runs that predate the
          per-case intervention counters simply yield nulls.
  matrix  Aggregate runs.jsonl + cases.jsonl into a markdown matrix whose rows
          are model x wire_hash and whose columns are pass rate, per-level
          rates and rescue-assisted passes.

Only the Python standard library is used.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
LEDGER_DIR = TOOLS_DIR.parent / "ledger"
RUNS_JSONL = LEDGER_DIR / "runs.jsonl"
CASES_JSONL = LEDGER_DIR / "cases.jsonl"


# ---------------------------------------------------------------- io helpers

def load_json(path, required=False):
    path = Path(path)
    if not path.is_file():
        if required:
            raise FileNotFoundError("missing required file: %s" % path)
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON in %s: %s" % (path, exc))


def read_jsonl(path):
    path = Path(path)
    if not path.is_file():
        return []
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            print("warning: %s:%d is not valid JSON, skipped" % (path, i), file=sys.stderr)
    return rows


def append_jsonl(path, row):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def now_utc_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ------------------------------------------------------------ derived fields

def derive_endpoint(model):
    """model.provider / model.completion -> endpoint string ('provider/completion')."""
    if not isinstance(model, dict):
        return None
    parts = [str(p) for p in (model.get("provider"), model.get("completion")) if p]
    return "/".join(parts) if parts else None


def protocol_invalid_rate(metrics, channel="text"):
    """1 - decision protocol validity rate for the run's channel.

    Text runs read decision_protocol_validity (falling back to
    protocol_validity); native runs read native_protocol_validity. A missing
    score (older runs, or a channel with no decision steps) yields None
    instead of crashing.
    """
    if not isinstance(metrics, dict):
        return None
    if channel == "native":
        keys = ("native_protocol_validity",)
    else:
        keys = ("decision_protocol_validity", "protocol_validity")
    for key in keys:
        score = metrics.get(key)
        if not isinstance(score, dict):
            continue
        total, correct, rate = score.get("total"), score.get("correct"), score.get("rate")
        if isinstance(total, (int, float)) and not isinstance(total, bool) and total > 0 \
                and isinstance(correct, (int, float)) and not isinstance(correct, bool):
            return round(max(0.0, min(1.0, 1.0 - correct / total)), 6)
        if isinstance(rate, (int, float)) and not isinstance(rate, bool):
            return round(max(0.0, min(1.0, 1.0 - rate)), 6)
    return None


def derive_channel(model):
    """model.completion -> step channel: chat-completions runs use structured
    provider tool calls ('native'); everything else is the text wire."""
    if isinstance(model, dict) and model.get("completion") == "chat-completions":
        return "native"
    return "text"


def group_rates(rows, key):
    out = {}
    for row in rows:
        val = row.get(key)
        group = out.setdefault(str(val) if val is not None else "unknown",
                               {"passed": 0, "total": 0})
        group["total"] += 1
        if row.get("passed"):
            group["passed"] += 1
    for group in out.values():
        group["rate"] = round(group["passed"] / group["total"], 4) if group["total"] else None
    return out


def trap_hit(final_output, decoys, tol=1e-6):
    """Return the trap id whose decoy value equals the final output, else None."""
    if not isinstance(decoys, dict) or not isinstance(final_output, str):
        return None
    out = final_output.strip()
    if not out:
        return None
    out_num = None
    try:
        out_num = float(out)
    except ValueError:
        pass
    for trap_id in sorted(decoys):
        val = decoys[trap_id]
        if val is None:
            continue
        if isinstance(val, str) and out == val:
            return trap_id
        if out_num is not None:
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                if abs(out_num - float(val)) <= tol:
                    return trap_id
            elif isinstance(val, str):
                try:
                    if abs(out_num - float(val)) <= tol:
                        return trap_id
                except ValueError:
                    pass
    return None


# ----------------------------------------------------------------- ingest

def build_run_row(manifest, summary, case_rows, args):
    model = manifest.get("model") or {}
    harness = manifest.get("harness") or {}
    sampling = manifest.get("sampling")
    if not isinstance(sampling, dict):
        sampling = None
    metrics = (summary or {}).get("metrics") or {}
    channel = derive_channel(model)
    date = manifest.get("completed_at") or manifest.get("started_at") or now_utc_iso()
    pass_mean = None
    ts = metrics.get("task_success")
    if isinstance(ts, dict) and isinstance(ts.get("rate"), (int, float)):
        pass_mean = round(ts["rate"], 6)
    elif case_rows:
        passed = sum(1 for r in case_rows if r["passed"])
        pass_mean = round(passed / len(case_rows), 6)
    return {
        "run_id": manifest.get("run_id") or (summary or {}).get("run_id"),
        "date": date,
        "config_name": args.config_name,
        "k_index": args.k_index,
        "model_id": model.get("identifier"),
        "model_fingerprint": model.get("fingerprint"),
        "state_sha256": harness.get("state_sha256"),
        "wire_profile": harness.get("wire_profile"),
        "wire_hash": harness.get("wire_hash"),
        "harness_version": harness.get("version"),
        "scorer_version": harness.get("scorer_version"),
        "tool_catalog": harness.get("tool_catalog"),
        "tool_catalog_hash": harness.get("tool_catalog_hash"),
        # Comparability keys: the full sampling object as recorded in run.json
        # (post-fix-6 manifests already omit the keys the backend rejected)
        # plus the loop budgets that change what a pass means.
        "sampling": sampling,
        "channel": channel,
        "case_parallelism": harness.get("case_parallelism"),
        "max_steps": harness.get("max_steps"),
        "duplicate_replay_limit": harness.get("duplicate_replay_limit"),
        "duplicate_rescue_threshold": harness.get("duplicate_rescue_threshold"),
        "same_tool_rescue_limit": harness.get("same_tool_rescue_limit"),
        "endpoint": derive_endpoint(model),
        "pass_mean": pass_mean,
        "pass_all_k": None,  # filled after all k replicas of a config are ingested
        "by_level": group_rates(case_rows, "level"),
        "by_scenario": group_rates(case_rows, "scenario"),
        "protocol_invalid_rate": protocol_invalid_rate(metrics, channel),
        "rescue_assisted_passes": sum(1 for r in case_rows
                                      if r["passed"] and (r.get("rescues") or 0) > 0),
        "bank_version": args.bank_version,
    }


def build_case_row(run_dir, summary_case, tags_by_id, args, run_id):
    case_id = summary_case.get("id")
    tags = summary_case.get("tags")
    if not isinstance(tags, dict) or not tags:
        tags = tags_by_id.get(case_id) or {}
    turns = [t for t in (summary_case.get("turns") or []) if isinstance(t, dict)]
    # failure strings: per-turn expectation failures plus case-level end-state failures
    failures = sum(len(t.get("failures") or []) for t in turns)
    failures += len(summary_case.get("failures") or [])
    tool_calls = summary_case.get("tool_calls")
    ref_calls = tags.get("ref_calls")
    redundancy = None
    if isinstance(tool_calls, (int, float)) and not isinstance(tool_calls, bool) \
            and isinstance(ref_calls, (int, float)) and not isinstance(ref_calls, bool) \
            and ref_calls:
        redundancy = round(tool_calls / ref_calls, 4)
    max_turns_hit = False
    for t in turns:
        result = t.get("result") or {}
        if isinstance(result, dict) and result.get("forced_answer_reason"):
            max_turns_hit = True
        runner_error = t.get("runner_error")
        if isinstance(runner_error, str) and "budget" in runner_error.lower():
            max_turns_hit = True
    final_output = None
    if turns:
        result = turns[-1].get("result") or {}
        if isinstance(result, dict):
            final_output = result.get("output")
    decoys = tags.get("trap_decoys")
    rescues = summary_case.get("rescues")
    return {
        "run_id": run_id,
        "config_name": args.config_name,
        "k_index": args.k_index,
        "case_id": case_id,
        "case_version": tags.get("version") if isinstance(tags.get("version"), int) else 1,
        "family": tags.get("family"),
        "level": tags.get("level"),
        "scenario": tags.get("scenario"),
        "passed": bool(summary_case.get("passed")),
        "failures": failures,
        "tool_calls": tool_calls if isinstance(tool_calls, (int, float)) else None,
        "ref_calls": ref_calls if isinstance(ref_calls, (int, float)) else None,
        "redundancy": redundancy,
        "max_turns_hit": max_turns_hit,
        "duplicate_rejects": summary_case.get("duplicate_rejects"),
        "rescues": rescues if isinstance(rescues, (int, float)) else None,
        "trap_hit": trap_hit(final_output, decoys),
        "trace_ref": "%s#%s" % (run_dir, case_id),
    }


def cmd_ingest(args):
    run_dir = args.run_dir.rstrip("/") or "."
    try:
        manifest = load_json(Path(args.run_dir) / "run.json", required=True)
        summary = load_json(Path(args.run_dir) / "summary.json", required=True)
    except (FileNotFoundError, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    if not isinstance(manifest, dict) or not isinstance(summary, dict):
        print("error: run.json/summary.json must be JSON objects", file=sys.stderr)
        return 2

    run_id = manifest.get("run_id") or summary.get("run_id")
    tags_by_id = {}
    for c in manifest.get("cases") or []:
        if isinstance(c, dict) and c.get("id") is not None:
            tags_by_id[c["id"]] = c.get("tags") or {}

    existing_runs = read_jsonl(RUNS_JSONL)
    existing_cases = read_jsonl(CASES_JSONL)
    run_key = (run_id, args.k_index)
    case_keys = {(r.get("run_id"), r.get("case_id"), r.get("k_index")) for r in existing_cases}

    new_case_rows = []
    for sc in summary.get("cases") or []:
        if not isinstance(sc, dict) or sc.get("id") is None:
            continue
        key = (run_id, sc["id"], args.k_index)
        if key in case_keys:
            continue
        new_case_rows.append(build_case_row(run_dir, sc, tags_by_id, args, run_id))

    skipped_cases = len([c for c in (summary.get("cases") or [])
                         if isinstance(c, dict) and c.get("id") is not None]) - len(new_case_rows)

    if any((r.get("run_id"), r.get("k_index")) == run_key for r in existing_runs):
        new_run_row = None
    else:
        new_run_row = build_run_row(manifest, summary, new_case_rows, args)

    if new_case_rows:
        for row in new_case_rows:
            append_jsonl(CASES_JSONL, row)
    if new_run_row is not None:
        append_jsonl(RUNS_JSONL, new_run_row)

    print("run_id=%s config=%s k=%s" % (run_id, args.config_name, args.k_index))
    print("runs.jsonl: %s" % ("+1 row" if new_run_row is not None else "skipped (already ingested)"))
    print("cases.jsonl: +%d rows (%d already present)"
          % (len(new_case_rows), max(skipped_cases, 0)))
    return 0


# ----------------------------------------------------------------- matrix

def _fmt_rate(passed, total):
    if not total:
        return "-"
    return "%.1f%% (%d/%d)" % (100.0 * passed / total, passed, total)


def cmd_matrix(args):
    runs = read_jsonl(RUNS_JSONL)
    cases = read_jsonl(CASES_JSONL)
    if args.bank_version is not None:
        runs = [r for r in runs if r.get("bank_version") == args.bank_version]
    run_ids = {r.get("run_id") for r in runs}
    cases = [c for c in cases if c.get("run_id") in run_ids]
    if not runs:
        print("no runs in ledger%s" % (" for bank_version %s" % args.bank_version
                                       if args.bank_version else ""))
        return 0

    groups = {}
    for r in runs:
        key = (str(r.get("model_id")), str(r.get("wire_hash") or "null"))
        groups.setdefault(key, set()).add(r.get("run_id"))

    print("# workbank matrix")
    print()
    print("| model | wire | runs | pass | L0 | L1 | L2 | L3 | rescue-assisted |")
    print("|---|---|---|---|---|---|---|---|---|")
    for (model_id, wire_hash), run_ids_in_group in sorted(groups.items()):
        rows = [c for c in cases if c.get("run_id") in run_ids_in_group]
        passed = sum(1 for c in rows if c.get("passed"))
        rescue_assisted = sum(1 for c in rows if c.get("passed") and (c.get("rescues") or 0) > 0)
        by_level = group_rates(rows, "level")
        level_cells = []
        for level in ("L0", "L1", "L2", "L3"):
            g = by_level.get(level)
            level_cells.append(_fmt_rate(g["passed"], g["total"]) if g else "-")
        print("| %s | %s | %d | %s | %s | %d |" % (
            model_id, wire_hash[:8] if len(wire_hash) > 8 else wire_hash,
            len(run_ids_in_group), _fmt_rate(passed, len(rows)),
            " | ".join(level_cells), rescue_assisted))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="workbank scoring ledger (runs.jsonl / cases.jsonl)")
    sub = ap.add_subparsers(dest="command", required=True)

    ap_ingest = sub.add_parser("ingest", help="ingest one run directory into the ledger")
    ap_ingest.add_argument("--config-name", required=True, help="logical config name for this run")
    ap_ingest.add_argument("--k-index", required=True, type=int, help="replica index (0-based) of this run")
    ap_ingest.add_argument("--bank-version", default=None,
                           help="bank_version the run was produced from (e.g. sha256:...)")
    ap_ingest.add_argument("run_dir", help="run directory containing run.json and summary.json")
    ap_ingest.set_defaults(func=cmd_ingest)

    ap_matrix = sub.add_parser("matrix", help="aggregate the ledger into a markdown matrix")
    ap_matrix.add_argument("--bank-version", default=None,
                           help="only include runs with this bank_version")
    ap_matrix.set_defaults(func=cmd_matrix)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
