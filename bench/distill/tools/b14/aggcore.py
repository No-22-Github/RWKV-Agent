"""Shared aggregation engine for the b14 bash cases (aggregate / precise-match /
long-file / recovery). A case is a table world (files + row generator) plus one
query per turn; the same AGG_SRC is exec'd here and embedded in verify.py, so
the answer the builder picks and the one verify recomputes cannot drift."""
import json
from random import Random

from common import REFS, case, lines, literal_free, thousands, verify_src

AGG_SRC = r'''
import json, re


def parse(fmt, text, cols, sep, header, pattern):
    out = []
    rows = text.splitlines()
    if fmt == "csv":
        if header:
            assert rows[0].split(sep) == cols, rows[0]
            rows = rows[1:]
        for line in rows:
            parts = line.split(sep)
            assert len(parts) == len(cols), line
            out.append(dict(zip(cols, parts)))
    elif fmt == "jsonl":
        for line in rows:
            out.append(json.loads(line))
    elif fmt == "kv":
        for line in rows:
            out.append(dict(tok.split("=", 1) for tok in line.split(" ")))
    elif fmt == "re":
        for line in rows:
            m = re.fullmatch(pattern, line)
            assert m, line
            out.append(m.groupdict())
    else:
        raise ValueError(fmt)
    return out


def ev(expr, r):
    return eval(expr, {"int": int, "float": float, "len": len, "str": str, "any": any, "re": re, "r": r})


def agg(q, rows):
    sel = [r for r in rows if ev(q["pred"], r)]
    kind = q["agg"]
    if kind == "count":
        return len(sel)
    if kind == "sum":
        return sum(int(ev(q["val"], r)) for r in sel)
    if kind == "sumc":
        cents = sum(int(round(float(ev(q["val"], r)) * 100)) for r in sel)
        return "%d.%02d" % (cents // 100, cents % 100)
    if kind == "distinct":
        return len({str(ev(q["val"], r)) for r in sel})
    if kind == "top":
        tally = {}
        for r in sel:
            key = str(ev(q["key"], r))
            tally[key] = tally.get(key, 0) + (int(ev(q["val"], r)) if q.get("val") else 1)
        ranked = sorted(tally.items(), key=lambda kv: -kv[1])
        if len(ranked) < 2 or ranked[0][1] - ranked[1][1] < q.get("margin", 2):
            raise ValueError("no clear leader")
        return ranked[0][0]
    if kind == "last":
        if not sel:
            raise ValueError("empty")
        return str(ev(q["val"], sel[-1]))
    raise ValueError(kind)
'''
_ns = {}
exec(AGG_SRC, _ns)
parse, agg, ev = _ns["parse"], _ns["agg"], _ns["ev"]


def render(world, r):
    fmt = world["fmt"]
    if fmt == "csv":
        return world.get("sep", ",").join(str(r[c]) for c in world["cols"])
    if fmt == "jsonl":
        return json.dumps(r, ensure_ascii=False)
    if fmt == "kv":
        return " ".join("%s=%s" % (c, r[c]) for c in world["cols"])
    if fmt == "re":
        return world["template"].format(**r)
    raise ValueError(fmt)


def make_files(world, rng):
    files, tables = {}, {}
    for fi, name in enumerate(world["files"]):
        n = rng.randint(*world["rows"])
        rows = [world["gen"](rng, fi, i) for i in range(n)]
        body = ([world.get("sep", ",").join(world["cols"])] if world["fmt"] == "csv" and world.get("header", True) else [])
        body += [render(world, r) for r in rows]
        path = world["root"] + "/" + name
        files[path] = lines(body)
        tables[path] = parse(world["fmt"], files[path], world.get("cols"), world.get("sep", ","),
                             world.get("header", True), world.get("pattern"))
    return files, tables


def fmt_val(v):
    return v if isinstance(v, str) else str(v)


def expect_for(v, kind, extra=None):
    """Turn expect for one answer: a number by whole token (both thousands
    spellings past 999), a name by substring."""
    e = {"max_output_chars": 600}
    if kind in ("top", "last"):
        e["output_contains"] = [v]
    else:
        forms = thousands(v)
        if len(forms) > 1:
            e["output_contains_any"] = forms
            e["output_contains_any_token"] = True
        else:
            e["output_contains"] = [forms[0]]
            e["output_contains_token"] = True
    if extra:
        e.update(extra)
    return e


VERIFY_TAIL = r'''
ALL = []
for path in DATA:
    ALL += parse(W["fmt"], case["files"][path], W["cols"], W["sep"], W["header"], W["pattern"])
for path, start in CHECKS.items():
    assert case["files"][path].startswith(start), path
vals = [agg(q, ALL if q.get("scope") is None else [r for p in q["scope"] for r in parse(W["fmt"], case["files"][p], W["cols"], W["sep"], W["header"], W["pattern"])]) for q in QS]
anyset = []
for q, v in zip(QS, vals):
    if q["agg"] not in ("top", "last"):
        s = str(v)
        whole, _, frac = s.partition(".")
        g = format(int(whole), ",") + ("." + frac if frac else "")
        if g != s:
            anyset += [s, g]
out = {}
if anyset:
    out["expected_contains_any"] = anyset
elif QS[-1]["agg"] in ("top", "last"):
    out["expected_string"] = vals[-1]
else:
    out["expected_number"] = float(vals[-1]) if "." in str(vals[-1]) else int(vals[-1])
print(json.dumps(out, ensure_ascii=False))
'''


def agg_case(cid, world, queries, *, sub, seed, desc, family, notes_extra="", traps=None,
             axes=("OBS",), extra_checks=None, task_type=None, spec_extra=None, prefix_files=None,
             first_scope=True, min_answer=5, case_expect=None, extra_decoys=None):
    """queries: one dict per turn with agg/pred/val/key, prompt, cmd (reference
    bash, one string), decoy (overrides for the loose reading), decoy_note."""
    if sub in ("M9a", "M9c", "M9g"):
        # every aggregation fixture is past read_file's 64KB in total, not just past bash's 8KB
        probe, _ = make_files(world, Random(seed))
        size = sum(len(t.encode()) for t in probe.values())
        if size < 70 * 1024:
            f = 70 * 1024 * 1.15 / size
            world = dict(world, rows=(int(world["rows"][0] * f) + 1, int(world["rows"][1] * f) + 1))
    for attempt in range(2000):
        rng = Random(seed * 7919 + attempt * 104729)
        files, tables = make_files(world, rng)
        if prefix_files:
            files.update(prefix_files)
        allrows = [r for t in tables.values() for r in t]
        first = next(iter(tables.values()))
        try:
            vals = [agg(q, allrows if q.get("scope") is None else [r for p in q["scope"] for r in tables[world["root"] + "/" + p]]) for q in queries]
            decs = [agg(dict(q, **q["decoy"]), allrows) if q.get("decoy") else None for q in queries]
            firsts = []
            for q in queries:
                try:
                    firsts.append(agg(q, first) if len(tables) > 1 and q.get("scope") is None else None)
                except ValueError:
                    firsts.append(None)
        except (ValueError, ZeroDivisionError):
            continue
        ok = len({fmt_val(v) for v in vals}) == len(vals)
        for q, v, d, f in zip(queries, vals, decs, firsts):
            if d is not None:
                ok = ok and fmt_val(d) != fmt_val(v)
            if f is not None and first_scope:
                ok = ok and fmt_val(f) != fmt_val(v)
            if q["agg"] in ("top", "last"):
                others = {str(ev(q.get("key") or q["val"], r)) for r in allrows} - {v}
                ok = ok and not any(v in o for o in others if o)
            else:
                ok = ok and float(v) >= min_answer and (attempt >= 300 or literal_free(files, v))
        if ok:
            break
    else:
        raise SystemExit("%s: no seed" % cid)
    data = [p for p in tables]
    W = {k: world.get(k) for k in ("fmt", "cols", "pattern")}
    W["sep"] = world.get("sep", ",")
    W["header"] = world.get("header", True)
    qs = [{k: v for k, v in q.items() if k in ("agg", "pred", "val", "key", "margin", "scope")} for q in queries]
    for q in qs:
        if q.get("scope"):
            q["scope"] = [world["root"] + "/" + p for p in q["scope"]]
    checks = dict(extra_checks or {})
    readme = world["root"] + "/" + world["readme_name"]
    files[readme] = lines(world["readme"])
    checks[readme] = world["readme"][0]
    body = AGG_SRC + "\nW = %r\nDATA = %r\nQS = %r\nCHECKS = %r\n" % (W, data, qs, checks) + VERIFY_TAIL
    verify = verify_src(files, body)
    size = sum(len(files[p].encode()) for p in data)
    traps = list(traps) if traps is not None else []
    decoys = {}
    if traps == [] and any(q.get("decoy") for q in queries):
        traps.append("TR-DECOY")
    if "TR-DECOY" in traps:
        decoys["TR-DECOY"] = next(fmt_val(d) for d in decs if d is not None)
    if len(tables) > 1 and firsts[-1] is not None and first_scope and "TR-MULTISRC" not in traps and len(traps) < 2:
        traps.append("TR-MULTISRC")
    if "TR-MULTISRC" in traps:
        decoys["TR-MULTISRC"] = fmt_val(firsts[-1])
    if "TR-TRUNC" in traps:
        # what a read cut at 64KB would give: the same query over the head rows
        head = []
        for p in data:
            cut = files[p].encode()[:64 * 1024].decode(errors="ignore")
            cut = cut[:cut.rfind("\n") + 1]
            head += parse(world["fmt"], cut, world.get("cols"), world.get("sep", ","), world.get("header", True), world.get("pattern"))
        try:
            decoys["TR-TRUNC"] = fmt_val(agg(queries[-1], head))
        except ValueError:
            decoys["TR-TRUNC"] = "UNKNOWN"
        if decoys["TR-TRUNC"] == fmt_val(vals[-1]):
            decoys["TR-TRUNC"] = "UNKNOWN"
    if extra_decoys:
        decoys.update(extra_decoys(tables, queries))
    for t in traps:
        decoys.setdefault(t, None)
    notes = "## Traps\n"
    for i, (q, v, d) in enumerate(zip(queries, vals, decs), 1):
        head = "Turn %d" % i if len(queries) > 1 else "Answer"
        notes += "- %s: %s." % (head, fmt_val(v))
        if d is not None:
            notes += " TR-DECOY: %s gives %s." % (q["decoy_note"], fmt_val(d))
        notes += "\n"
    if "TR-MULTISRC" in traps:
        notes += "- TR-MULTISRC: %d files; the first one alone gives %s.\n" % (len(tables), fmt_val(firsts[-1]))
    notes += "- Data volume: %d data files, %d KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.\n" % (len(data), size // 1024)
    notes += notes_extra
    notes += "\n## Reference solution\n"
    for i, q in enumerate(queries, 1):
        notes += "%s bash: `%s` -> %s\n" % ("Turn %d:" % i if len(queries) > 1 else "1.", q["cmd"], fmt_val(vals[i - 1]))
    notes += "Final answer%s: %s\n" % ("" if len(queries) == 1 else " (last turn)", queries[-1]["reply"].format(v=fmt_val(vals[-1])))
    notes += "\n## Why the answer is unique\n%s\n" % world["unique"]
    turns = []
    for q, v in zip(queries, vals):
        turns.append({"prompt": q["prompt"], "expect": expect_for(fmt_val(v), q["agg"])})
    spec = {"kind": "bash_aggregate", "needs": [readme] if world.get("needs_readme") else []}
    spec.update(spec_extra or {})
    refcmds = [q["cmd"] for q in queries]
    path = case(cid, sub=sub, spec=spec, desc=desc, task_type=task_type or world["task_type"], family=family,
                ref_calls=len(queries), files=files, turns=turns, verify=verify, notes=notes, traps=traps,
                decoys=decoys, axes=axes, **({"case_expect": case_expect(files) if callable(case_expect) else case_expect} if case_expect else {}))
    # each turn's command is checked on its own against that turn's answer (build.py)
    REFS[cid] = (files, refcmds, [fmt_val(v) for v in vals])
    return path


def Q(agg, pred, prompt, cmd, reply, *, val=None, key=None, decoy=None, decoy_note="", scope=None, margin=None):
    q = {"agg": agg, "pred": pred, "prompt": prompt, "cmd": cmd, "reply": reply, "decoy_note": decoy_note}
    if val:
        q["val"] = val
    if key:
        q["key"] = key
    if decoy:
        q["decoy"] = decoy
    if scope:
        q["scope"] = scope
    if margin:
        q["margin"] = margin
    return q
