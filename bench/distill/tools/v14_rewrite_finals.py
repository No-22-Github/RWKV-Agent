#!/usr/bin/env python3
"""M1: Rewrite stock pure-value final answers into natural 1-2 sentence explanations.

Follows bench/distill/v1.4/distill-allocation-v1.4.md §3.1.
Usage:
  v14_rewrite_finals.py prepare --out-dir bench/distill/v1.4/b09_work
  v14_rewrite_finals.py validate --work-dir bench/distill/v1.4/b09_work
  v14_rewrite_finals.py apply --work-dir bench/distill/v1.4/b09_work --out-script bench/distill/v1.4/teacher/b09-m1.jsonl
"""
import argparse
import glob
import json
import os
import random
import re
from collections import Counter, defaultdict

from distill_paths import EXCLUDE_JSONL, REPO, case_files, teacher_script, version_dir
B05_SCRIPT = teacher_script("v1.3", "b05-baseline")
SUMMARY_JSON = os.path.join(REPO, "local", "runs", "distill", "v13-clean", "b05", "run", "summary.json")
# v1.3 N10 closeout script (rows source distill-b08).
B08_SCRIPT = os.path.join(REPO, "local", "runs", "distill", "v13-clean", "closeout.jsonl")
PATH_SUFFIXES = ("p90", "p92")

CONTRACT_PATTERNS = [
    r'\s*Reply with only the final answer\. If you cannot determine the answer, reply exactly UNKNOWN\.',
    r'\s*Reply with only the final answer\.',
    r'\s*If you cannot determine the answer, reply exactly UNKNOWN\.',
    r'\s*Give the number alone, as digits, with no label\.?',
    r'\s*Give the answer as a single number, with no unit in the reply\.?',
    r'\s*Give the count alone, as digits, with no label\.?',
    r'\s*Give the count as a number alone\.?',
    r'\s*Give the file path on its own, with the \.py suffix\.?',
    r'\s*Answer with the module\'s file path alone, including its \.py suffix\.?',
    r'\s*Answer with the code alone\.?',
    r'\s*Just the number\.?',
    r'\s*Just the answer\.?',
    r'\s*只回数字[。！]?',
    r'\s*只回复最终答案[。！]?',
    r'\s*只给出最终答案[。！]?',
    r'\s*仅输出最终答案[。！]?'
]

# Selection keys on CONTRACT_PATTERNS alone so the 450 picks stay fixed. The
# rewrites below catch the remaining "value only" phrasings that would
# contradict a sentence-length final answer; formatting asks that a sentence
# can still honour ("as HH:MM", "exactly as the index writes it") stay.
EXTRA_CLEAN = [
    (r'\s*Answer with (?:the|its) [^.]*?\balone\.', ''),
    (r'\s*Give the [^.]*?\balone\b[^.]*?\bwith (?:no label|nothing else)\.', ''),
    (r'\s*Give the answer as a number alone\.', ''),
    (r' as a number alone\.', '.'),
    (r', as a single number in ([^.]+?) with no unit in the reply\.', r' in \1.'),
    (r', as a single number with no unit in the reply\.', '.'),
    (r', without the % sign \([^)]*\)', ''),
]

# A cleaned prompt must not match any of these; validate/apply refuse otherwise.
RESIDUAL_CONTRACT = re.compile(
    r'reply with only|reply exactly|UNKNOWN|\b(?:answer|give)\b[^.]*\balone\b|with no label|with nothing else'
    r'|no unit in the reply|without the % sign|just the (?:number|answer)|只回|只给出|仅输出',
    re.I,
)


def clean_prompt(prompt):
    s = prompt
    for pat in CONTRACT_PATTERNS:
        s = re.sub(pat, '', s, flags=re.I)
    for pat, repl in EXTRA_CLEAN:
        s = re.sub(pat, repl, s, flags=re.I)
    return s.strip()


def value_in_text(value, text):
    """The value must appear as its own token: "5" inside "2026-05" or "7.5" does not count."""
    v = value.strip()
    variants = {v, v.replace(',', '')}
    norm = normalize_number_str(v)
    if re.fullmatch(r'-?\d+(\.\d+)?', norm):
        variants |= {norm, f"{float(norm):,}".rstrip('0').rstrip('.') if '.' in norm else f"{int(float(norm)):,}"}
    for cand in variants:
        if cand and re.search(r'(?<![0-9A-Za-z])(?<!\d[.,])' + re.escape(cand) + r'(?![0-9A-Za-z])(?![.,]\d)', text):
            return True
    return False


def is_chinese(text):
    return len(re.findall(r'[\u4e00-\u9fff]', text)) >= 3


def normalize_number_str(s):
    clean = s.strip().replace(',', '')
    try:
        val = float(clean)
        if val.is_integer():
            return str(int(val))
        return f"{val:g}"
    except ValueError:
        return s.strip()


def extract_numbers(text):
    nums = set()
    # Find decimal or integer numbers
    for m in re.finditer(r'-?\b\d+(?:,\d{3})*(?:\.\d+)?\b', text):
        raw = m.group(0).replace(',', '')
        nums.add(raw)
        try:
            f = float(raw)
            if f.is_integer():
                nums.add(str(int(f)))
            nums.add(f"{f:g}")
        except ValueError:
            pass
    return nums


def validate_rewritten(original_val, cleaned_prompt, tool_steps, rewritten_text, lang):
    """Mechanical validation according to §3.1 step 5."""
    text = rewritten_text.strip()
    if not text:
        return False, "empty text"

    # 1. Length <= 300 chars
    if len(text) > 300:
        return False, f"length {len(text)} > 300"

    # 2. No leaked tags / role labels / flower
    leak_patterns = [r'<tool_call>', r'<tool_response>', r'Assistant:', r'User:', r'System:', r'✿']
    for pat in leak_patterns:
        if re.search(pat, text):
            return False, f"leaked pattern {pat}"

    # 3. Contains original value as a token (allow thousands-separator difference)
    if not value_in_text(original_val, text):
        return False, f"original value {original_val!r} not in rewritten text"
    if RESIDUAL_CONTRACT.search(cleaned_prompt):
        return False, "cleaned prompt still carries an answer contract"

    # 4. File paths mentioned in text must have been read in trajectory
    read_paths = set()
    for st in tool_steps:
        if st.get("action_type") == "tool" and st.get("tool") in ("read_file", "read_lines", "data_query"):
            args = st.get("tool_arguments", {})
            p = args.get("path")
            if p:
                read_paths.add(p)
                read_paths.add(os.path.basename(p))

    # Ground truth answer itself may be a file/module path
    orig_clean = original_val.strip()
    read_paths.add(orig_clean)
    read_paths.add(os.path.basename(orig_clean))

    # Look for path-like substrings in text (e.g. dir/file.ext or file.ext)
    # Matches words containing / or common file extensions
    KNOWN_UNITS = {"km/h", "m/s", "mi/h", "mph", "rev/min", "l/min", "litres/day", "litres/week", "units/hour", "units/day", "deg/s"}
    path_matches = re.findall(r'\b[A-Za-z0-9_\-\u4e00-\u9fff]+(?:/[A-Za-z0-9_\-\u4e00-\u9fff.]+)+\b|\b[A-Za-z0-9_\-\u4e00-\u9fff]+\.(?:yaml|yml|json|env|txt|csv|tsv|md|py|go|toml|ini|conf)\b', text)
    for p in path_matches:
        if p.lower() in KNOWN_UNITS or re.match(r'^\d{4}/\d{2}/\d{2}$', p):
            continue
        if p not in read_paths and os.path.basename(p) not in read_paths:
            return False, f"unverified file path {p} not among read paths {read_paths}"

    # 5. Numbers mentioned must come from original value, prompt, or tool results
    allowed_numbers = set()
    allowed_numbers |= extract_numbers(original_val)
    allowed_numbers |= extract_numbers(cleaned_prompt)
    for st in tool_steps:
        res = st.get("tool_result", "")
        allowed_numbers |= extract_numbers(str(res))

    mentioned_numbers = extract_numbers(text)
    for num in mentioned_numbers:
        # Ignore small single-digit sentence numbers like 1 or 2 if used grammatically (e.g. "第一", "1-2")
        if num not in allowed_numbers and num not in {"1", "2"}:
            return False, f"invented number {num} not in evidence"

    # 6. Language matches prompt
    prompt_is_zh = is_chinese(cleaned_prompt)
    text_is_zh = is_chinese(text)
    if prompt_is_zh != text_is_zh:
        return False, f"language mismatch: prompt zh={prompt_is_zh}, text zh={text_is_zh}"

    return True, "ok"


def load_b05_data():
    case_map = {}
    for path in case_files():
        try:
            c = json.load(open(path))
            case_map[c["id"]] = (path, c)
        except Exception:
            pass

    summary_map = {}
    if os.path.exists(SUMMARY_JSON):
        with open(SUMMARY_JSON) as f:
            data = json.load(f)
            for c in data.get("cases", []):
                summary_map[c["id"]] = c

    b05_paths = []
    with open(B05_SCRIPT) as f:
        for line in f:
            b05_paths.append(json.loads(line))

    return case_map, summary_map, b05_paths


def select_450_candidates(case_map, summary_map, b05_paths):
    family_paths = defaultdict(list)
    for p in b05_paths:
        cid = p["case_id"].split("--")[0]
        if cid not in case_map or p["case_id"] not in summary_map:
            continue
        cpath, case = case_map[cid]
        if len(case.get("turns", [])) != 1:
            continue
        prompt = case["turns"][0]["prompt"]
        final = p["outputs"][-1]["text"].strip()
        if len(final) > 80:
            continue
        if not any(re.search(pat, prompt, re.I) for pat in CONTRACT_PATTERNS):
            continue
        fam = case.get("tags", {}).get("family", "unknown")
        family_paths[fam].append((p, cpath, case, summary_map[p["case_id"]]))

    rng = random.Random(42)
    selected = []
    families = sorted(family_paths.keys())
    # Round 1: 1 per family
    for fam in families:
        selected.append(family_paths[fam][0])

    # Round 2: 2nd path from families with >= 2 paths
    rem = 450 - len(selected)
    multis = [fam for fam in families if len(family_paths[fam]) >= 2]
    rng.shuffle(multis)
    for fam in multis[:rem]:
        selected.append(family_paths[fam][1])

    return selected


def cmd_prepare(args):
    os.makedirs(args.out_dir, exist_ok=True)
    case_map, summary_map, b05_paths = load_b05_data()
    selected = select_450_candidates(case_map, summary_map, b05_paths)
    print(f"Selected {len(selected)} paths across {len(set(c[2]['tags']['family'] for c in selected))} families.")

    tasks = []
    for item in selected:
        p, cpath, case, s_case = item
        cid = case["id"]
        path_id = p["case_id"]
        orig_val = p["outputs"][-1]["text"].strip()
        orig_prompt = case["turns"][0]["prompt"]
        clean_p = clean_prompt(orig_prompt)
        steps = s_case["turns"][0]["result"].get("steps", [])
        tool_steps = [st for st in steps if st.get("action_type") == "tool"]

        # Compact representation of tools & read contents for LLM
        tools_summary = []
        read_files_evidence = {}
        for st in tool_steps:
            tool_name = st.get("tool")
            tool_args = st.get("tool_arguments", {})
            res = st.get("tool_result", {})
            if tool_name in ("read_file", "read_lines", "data_query"):
                fpath = tool_args.get("path")
                content = ""
                if isinstance(res, dict):
                    content = res.get("content", str(res.get("result", "")))
                else:
                    content = str(res)
                if fpath:
                    # truncate huge files to relevant lines if possible
                    read_files_evidence[fpath] = content[:3000]
            tools_summary.append({
                "tool": tool_name,
                "arguments": tool_args,
            })

        tasks.append({
            "case_id": cid,
            "path_id": path_id,
            "family": case.get("tags", {}).get("family", ""),
            "original_prompt": orig_prompt,
            "cleaned_prompt": clean_p,
            "original_value": orig_val,
            "is_chinese": is_chinese(clean_p),
            "tool_calls": tools_summary,
            "evidence": read_files_evidence,
            "tool_steps": tool_steps,
        })

    # Save all tasks
    all_path = os.path.join(args.out_dir, "all_tasks.json")
    with open(all_path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

    # Split into batches of 50
    batch_size = 50
    num_batches = (len(tasks) + batch_size - 1) // batch_size
    for i in range(num_batches):
        batch = tasks[i * batch_size : (i + 1) * batch_size]
        batch_path = os.path.join(args.out_dir, f"batch_{i}.json")
        with open(batch_path, "w", encoding="utf-8") as f:
            json.dump(batch, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(tasks)} tasks into {num_batches} batches under {args.out_dir}.")


def cmd_validate(args):
    all_tasks_path = os.path.join(args.work_dir, "all_tasks.json")
    if not os.path.exists(all_tasks_path):
        print(f"Cannot find {all_tasks_path}")
        return 1
    tasks = {t["path_id"]: t for t in json.load(open(all_tasks_path))}

    # Collect answers from batch outputs
    output_files = sorted(glob.glob(os.path.join(args.work_dir, "batch_*_out.json")))
    if not output_files:
        print(f"No batch_*_out.json found in {args.work_dir}")
        return 1

    answers = {}
    for f in output_files:
        data = json.load(open(f))
        for k, v in data.items():
            answers[k] = v

    print(f"Loaded {len(answers)} rewritten answers from {len(output_files)} batch output files.")
    passed = 0
    failed = 0
    fail_reasons = Counter()

    for path_id, text in answers.items():
        if path_id not in tasks:
            continue
        task = tasks[path_id]
        ok, reason = validate_rewritten(
            task["original_value"],
            task["cleaned_prompt"],
            task["tool_steps"],
            text,
            task["is_chinese"],
        )
        if ok:
            passed += 1
        else:
            failed += 1
            fail_reasons[reason] += 1
            print(f"FAIL {path_id}: {reason} | Text: {text}")

    total = passed + failed
    print(f"\nMechanical validation summary: {passed}/{total} passed ({100*passed/total:.1f}%), {failed} failed.")
    for r, count in fail_reasons.most_common():
        print(f"  {r}: {count}")
    return 0 if failed == 0 else 1


def cmd_apply(args):
    all_tasks_path = os.path.join(args.work_dir, "all_tasks.json")
    tasks = {t["path_id"]: t for t in json.load(open(all_tasks_path))}

    answers = {}
    for f in sorted(glob.glob(os.path.join(args.work_dir, "batch_*_out.json"))):
        answers.update(json.load(open(f)))

    case_map, _, b05_paths = load_b05_data()
    b05_by_id = {p["case_id"]: p for p in b05_paths}

    # pack drops a row only when an entry names its own batch (or none), so
    # "already excluded" has to be checked per (case_id, batch).
    existing = set()
    if os.path.exists(EXCLUDE_JSONL):
        for line in open(EXCLUDE_JSONL):
            row = json.loads(line)
            existing.add((row.get("case_id"), row.get("batch", "")))

    # Old paths that render from the rewritten case files: every b05 path, and
    # the b08 closeout paths (--p81) built from them. Re-rendered under the
    # contract-free prompt they would pair it with a bare value.
    old_paths = defaultdict(list)
    for p in b05_paths:
        old_paths[p["case_id"].split("--")[0]].append(("b05", p["case_id"]))
    for line in open(B08_SCRIPT):
        pid = json.loads(line)["case_id"]
        old_paths[pid.split("--")[0]].append(("b08", pid))

    passed = defaultdict(list)
    for path_id, text in sorted(answers.items()):
        if path_id not in tasks:
            continue
        task = tasks[path_id]
        ok, reason = validate_rewritten(
            task["original_value"], task["cleaned_prompt"], task["tool_steps"], text, task["is_chinese"])
        if not ok:
            print(f"Skipping failed case {path_id}: {reason}")
            continue
        passed[task["case_id"]].append((path_id, text))

    new_script_rows = []
    excludes_to_add = []
    for cid in sorted(passed):
        paths = passed[cid]
        if len(paths) > len(PATH_SUFFIXES):
            raise SystemExit(f"{cid}: {len(paths)} rewritten paths, only {len(PATH_SUFFIXES)} suffixes")
        task = tasks[paths[0][0]]

        cpath, case = case_map[cid]
        turn = case["turns"][0]
        turn["prompt"] = task["cleaned_prompt"]
        exp = turn.get("expect", {})
        for k in ("expected_number", "tolerance", "output_equals", "output_equals_any"):
            exp.pop(k, None)
        # Two paths of one case can spell the value differently ("£144.00" / "144.00");
        # check for the shortest spelling that every path's value contains.
        values = [tasks[pid]["original_value"].strip() for pid, _ in paths]
        common = [v for v in sorted(values, key=len) if all(v in w for w in values)]
        exp["output_contains"] = [common[0] if common else values[0]]
        # Short values ("5", "95") also occur inside dates and longer numbers; a
        # wrong final would still pass a plain substring check.
        exp["output_contains_token"] = True
        exp["max_output_chars"] = 300
        turn["expect"] = exp
        case["tags"]["answer_style"] = "natural"
        case["tags"]["version"] = case["tags"].get("version", 1) + 1
        with open(cpath, "w", encoding="utf-8") as f:
            f.write(json.dumps(case, indent=2, ensure_ascii=False) + "\n")

        for batch, old_id in old_paths[cid]:
            if (old_id, batch) not in existing:
                excludes_to_add.append({"batch": batch, "case_id": old_id, "reason": "v1.4 M1 改写终答"})
                existing.add((old_id, batch))

        # Sorted path ids: the first rewritten path becomes --p90, the second --p92
        # (--p91 is reserved for the v1.4 N10 closeout copies).
        for suffix, (path_id, text) in zip(PATH_SUFFIXES, paths):
            orig = b05_by_id[path_id]
            outputs = [dict(o) for o in orig["outputs"][:-1]]
            outputs.append({"text": text.strip(), "supervised": orig["outputs"][-1].get("supervised", True)})
            new_script_rows.append({"case_id": f"{cid}--{suffix}", "outputs": outputs})

    new_script_rows.sort(key=lambda r: r["case_id"])
    os.makedirs(os.path.dirname(args.out_script), exist_ok=True)
    with open(args.out_script, "w", encoding="utf-8") as f:
        for r in new_script_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {len(new_script_rows)} paths to {args.out_script}")

    with open(EXCLUDE_JSONL, "a", encoding="utf-8") as f:
        for ex in excludes_to_add:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"Appended {len(excludes_to_add)} exclusions to {EXCLUDE_JSONL}: "
          f"{dict(Counter(e['batch'] for e in excludes_to_add))}")
    print(f"Updated {len(passed)} case.json files.")


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd")

    p_prep = subparsers.add_parser("prepare")
    p_prep.add_argument("--out-dir", default=version_dir("v1.4", "b09_work"))

    p_val = subparsers.add_parser("validate")
    p_val.add_argument("--work-dir", default=version_dir("v1.4", "b09_work"))

    p_app = subparsers.add_parser("apply")
    p_app.add_argument("--work-dir", default=version_dir("v1.4", "b09_work"))
    p_app.add_argument("--out-script", default=teacher_script("v1.4", "b09-m1"))

    args = parser.parse_args()
    if args.cmd == "prepare":
        cmd_prepare(args)
    elif args.cmd == "validate":
        cmd_validate(args)
    elif args.cmd == "apply":
        cmd_apply(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
