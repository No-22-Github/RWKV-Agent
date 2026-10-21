"""b21e (v2.1: tabular data worked out with bash) shared framework.

A case spec is: fixture table (generated with a fixed seed), per-turn
(prompt, python calc source, answer kind, bash reference commands).
The calc source runs on the parsed fixture in build.py and again inside the
case's verify.py; build.py also replays the bash reference in the just-bash
sidecar and requires the sandbox output to agree with the python value.
"""
import base64
import csv
import hashlib
import io
import json
import os
import random
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch, Sidecar  # noqa: E402

BATCH = Batch(salt="b21e", author="llm:claude-sonnet-b21e", version="v2.1", tool_catalog="agent-tool-v2.0")
EXTRA = {"batch": "b21e"}
META = {}

# ---------------------------------------------------------------- column generators
# gen(rng, i, row) -> str ; row holds the already generated cells by header


def ID(prefix, width=4, start=1):
    return lambda g, i, r: "%s%0*d" % (prefix, width, start + i)


def C(vals, weights=None):
    return lambda g, i, r: g.choices(vals, weights=weights)[0] if weights else g.choice(vals)


def I(lo, hi):
    return lambda g, i, r: str(g.randint(lo, hi))


def M(lo, hi, dp=2, thousands=False):
    def f(g, i, r):
        cents = g.randint(int(lo * 100), int(hi * 100))
        v = cents / 100.0
        s = "%.*f" % (dp, v)
        if thousands:
            whole, _, frac = s.partition(".")
            s = "{:,}".format(int(whole)) + ("." + frac if frac else "")
        return s
    return f


def D(y, m1, m2, fmt="%Y-%m-%d"):
    import datetime
    def f(g, i, r):
        m = g.randint(m1, m2)
        d = g.randint(1, 28)
        return datetime.date(y, m, d).strftime(fmt)
    return f


def F(fn):
    """custom: fn(g, row) -> str"""
    return lambda g, i, r: fn(g, r)


def gen_rows(seed, cols, n):
    g = random.Random(seed)
    header = [c[0] for c in cols]
    rows = []
    for i in range(n):
        row = {}
        for name, fn in cols:
            row[name] = fn(g, i, row)
        rows.append([row[h] for h in header])
    return header, rows


def render(header, rows, delim=",", preamble=(), trail=0):
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=delim, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        w.writerow(r)
    return "".join(p + "\n" for p in preamble) + buf.getvalue() + "\n" * trail


# ---------------------------------------------------------------- parse + forms (shared source)
SHARED_SRC = '''
import csv, io
from collections import Counter, defaultdict

def parse(text, delim):
    lines = [l for l in text.split("\\n") if l.strip() != "" and not l.startswith("#")]
    rd = list(csv.reader(lines, delimiter=delim))
    head = rd[0]
    return [dict(zip(head, r)) for r in rd[1:]], head

def N(s):
    return float(s.replace(",", ""))

def forms(v, dp):
    if dp == 0:
        s = str(int(round(v)))
        out = [s]
        if abs(int(s)) >= 1000:
            out.append("{:,}".format(int(s)))
        return out
    s = "%.*f" % (dp, v)
    whole, _, frac = s.partition(".")
    out = [s]
    g = "{:,}".format(int(whole)) + "." + frac
    if "-" in whole and int(whole) == 0:
        g = "-0." + frac
    if g != s:
        out.append(g)
    t = s.rstrip("0").rstrip(".")
    if t != s:
        out.append(t)
        tg = g.rstrip("0").rstrip(".")
        if tg != t:
            out.append(tg)
    return list(dict.fromkeys(out))
'''
_ns = {}
exec(SHARED_SRC, _ns)
parse, N, forms = _ns["parse"], _ns["N"], _ns["forms"]


def run_calc(calc_src, R, extra=None):
    env = dict(_ns)
    env["R"] = R
    env.update(extra or {})
    exec(calc_src, env)
    return env["result"]


# ---------------------------------------------------------------- policies
def policy(idx, reader):
    """idx-based: every third case forces bash by hiding calculator and data_query."""
    p = {"must_offer": ["bash", reader]}
    if idx % 3 == 0:
        p["never_offer"] = ["calculator", "data_query"]
    return p


def is_zh(text):
    return len(re.findall(r"[一-鿿]", text)) >= 4


def level_for(n_traps, ref_calls, n_files, multi):
    if n_traps == 1 and ref_calls <= 4:
        return "L1"
    if n_traps == 2 or (n_traps == 1 and (n_files >= 3 or ref_calls >= 5)):
        return "L2"
    if n_traps >= 3 or (multi and n_traps >= 1) or ref_calls >= 8:
        return "L3"
    raise ValueError((n_traps, ref_calls))


def guard(files):
    d = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return ("import hashlib, json\n"
            "case = json.load(open(\"case.json\"))\n"
            "_pin = hashlib.sha256(json.dumps(case[\"files\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
            "assert _pin == %r, \"fixture changed\"\n" % d)


# ---------------------------------------------------------------- reference replay
def _read(sc, root, path):
    sc.next += 1
    sc.proc.stdin.write(json.dumps({"id": sc.next, "root": root, "op": "read", "path": path}) + "\n")
    sc.proc.stdin.flush()
    reply = json.loads(sc.proc.stdout.readline())
    if reply.get("error"):
        return None
    return base64.b64decode(reply["data"]).decode("utf-8")


def check_refs(sc, cid, files, turn_refs, expects):
    """turn_refs: list of command lists; expects: list of (kind, value, extra)."""
    root = os.path.realpath(tempfile.mkdtemp(prefix="b21e-ref-"))
    try:
        for p, t in files.items():
            tgt = os.path.join(root, p)
            os.makedirs(os.path.dirname(tgt), exist_ok=True)
            with open(tgt, "w", encoding="utf-8") as f:
                f.write(t)
        for ti, (cmds, (kind, val, extra)) in enumerate(zip(turn_refs, expects)):
            out = ""
            for c in cmds:
                r = sc.run(root, c)
                if r.get("error") or r.get("exit_code") not in (0, 1):
                    raise SystemExit("%s turn %d: `%s` -> %s" % (cid, ti + 1, c, r))
                out = r["stdout"] if kind != "files" else out + r["stdout"]
            if kind in ("int", "num"):
                primary = val[0]
                if not re.search(r"(?<![\d.,])" + re.escape(primary) + r"(?![\d]|\.\d)", out):
                    raise SystemExit("%s turn %d: sandbox stdout %r lacks %s" % (cid, ti + 1, out[:300], primary))
            elif kind == "names":
                pos = []
                for n in val:
                    k = out.find(n)
                    if k < 0:
                        raise SystemExit("%s turn %d: stdout %r lacks %s" % (cid, ti + 1, out[:300], n))
                    pos.append(k)
                if pos != sorted(pos):
                    raise SystemExit("%s turn %d: names out of order %r" % (cid, ti + 1, out[:300]))
            elif kind == "files":
                got = _read(sc, root, extra["path"])
                if got != val:
                    raise SystemExit("%s turn %d: file %s = %r want %r" % (cid, ti + 1, extra["path"], (got or "")[:300], val[:300]))
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ---------------------------------------------------------------- case writer
_SC = []


def sidecar():
    if not _SC:
        _SC.append(Sidecar())
    return _SC[0]


def close_sidecar():
    if _SC:
        _SC[0].close()


def make(cid, *, sub, desc, traps, path, header, rows, turns, delim=",", preamble=(), trail=0,
         reader="read_file", ref_calls=3, axes=("OBS",), notes_traps=(), extra_files=None, pol=None):
    """turns: list of dicts(prompt, calc, kind, dp, ref, out=(path, delim), excl)."""
    text = render(header, rows, delim, preamble, trail)
    files = {path: text}
    files.update(extra_files or {})
    R, head = parse(text, delim)
    assert head == header and len(R) == len(rows), cid
    nrows = len(rows)
    tl, expects, refs, srcs = [], [], [], []
    rules = {}
    scalar_forms = []
    first_name = None
    out_files = {}
    for t in turns:
        res = run_calc(t["calc"], R)
        kind = t["kind"]
        exp = {}
        if kind in ("int", "num"):
            dp = 0 if kind == "int" else t["dp"]
            fl = forms(res, dp)
            exp["output_contains_any"] = fl
            exp["output_contains_any_token"] = True
            for x in fl:
                if x not in scalar_forms:
                    scalar_forms.append(x)
            expects.append((kind, fl, None))
        elif kind == "names":
            assert len(set(res)) == len(res) and len(res) >= 2, cid
            exp["output_contains"] = list(res)
            exp["output_contains_token"] = True
            first_name = first_name or res[0]
            expects.append((kind, list(res), None))
        elif kind == "files":
            op, od = t["out"]
            content = render(res[0], res[1:], od)
            out_files[op] = content
            rules[op] = {"equals": content}
            expects.append((kind, content, {"path": op}))
        else:
            raise ValueError(kind)
        if t.get("excl"):
            exp["output_excludes"] = t["excl"]
        tl.append({"prompt": t["prompt"], "expect": exp})
        refs.append(t["ref"])
        srcs.append(t["calc"])
    for p, c in files.items():
        if p not in out_files:
            rules[p] = {"unchanged": True}
    ce = {"files": rules} if out_files else None
    for p in out_files:
        assert os.path.dirname(p) == os.path.dirname(path), cid
    check_refs(sidecar(), cid, files, refs, expects)

    body = SHARED_SRC + "\ntext = case[\"files\"][%r]\nR, head = parse(text, %r)\n" % (path, delim)
    body += "CALCS = %r\nKINDS = %r\nDPS = %r\nOUTS = %r\n" % (
        srcs, [t["kind"] for t in turns], [t.get("dp", 0) for t in turns], [t.get("out") for t in turns])
    body += '''
forms_all, names, outs = [], [], {}
for src, kind, dp, out in zip(CALCS, KINDS, DPS, OUTS):
    env = {"R": R, "N": N, "Counter": Counter, "defaultdict": defaultdict}
    exec(src, env)
    res = env["result"]
    if kind in ("int", "num"):
        forms_all += [x for x in forms(res, 0 if kind == "int" else dp) if x not in forms_all]
    elif kind == "names":
        names += res
    else:
        buf = io.StringIO()
        w = csv.writer(buf, delimiter=out[1], lineterminator="\\n")
        for row in res:
            w.writerow(row)
        outs[out[0]] = buf.getvalue()
if forms_all:
    print(json.dumps({"expected_contains_any": forms_all, "names": names, "files": outs}, ensure_ascii=False))
elif outs:
    print(json.dumps({"files": outs}, ensure_ascii=False))
else:
    print(json.dumps({"expected_string": names[0], "names": names}, ensure_ascii=False))
'''
    last = turns[-1]
    lres = run_calc(last["calc"], R)
    if last["kind"] in ("int", "num"):
        decoy = "%.*f" % (0 if last["kind"] == "int" else last["dp"], lres + 1)
    elif last["kind"] == "names":
        decoy = "no such name"
    else:
        decoy = "wrong file"
    multi = len(turns) > 1
    level = level_for(len(traps), ref_calls, len(files), multi)
    n = int(cid.split("-")[1])
    pol = pol or policy(n, reader)
    fam = "b21e-%s-%s" % (sub, cid.split("-")[1])
    notes = "## Traps\n" + "".join("- %s\n" % x for x in notes_traps)
    notes += "- fixture: %s, %d data rows, delimiter %r\n" % (path, nrows, delim)
    notes += "\n## Reference solution\n(each command replayed in the just-bash sandbox by build.py)\n"
    for i, t in enumerate(turns, 1):
        notes += "Turn %d:\n" % i + "".join("    %s\n" % c for c in t["ref"])
    notes += "\n## Why the answer is unique\nverify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.\n"
    BATCH.write_case(cid, desc=desc, task_type={"int": "filter_count", "num": "aggregate", "names": "rank", "files": "write_summary"}[turns[-1]["kind"]],
                     family=fam, level=level, ref_calls=ref_calls, files=files, turns=tl,
                     verify=guard(files) + body, notes=notes, traps=list(traps), decoys={t: decoy for t in traps},
                     axes=list(dict.fromkeys(list(axes))), case_expect=ce, answer_style="natural",
                     tool_policy=pol, extra_tags=dict(EXTRA, sub=sub))
    META[cid] = {"sub": sub, "lang": "zh" if is_zh(" ".join(t["prompt"] for t in turns)) else "en",
                 "turns": len(turns), "never": "never_offer" in pol, "level": level}


def ci(header, name):
    return header.index(name) + 1


def T(prompt, calc, kind, ref, dp=0, out=None, excl=None):
    d = {"prompt": prompt, "calc": calc, "kind": kind, "ref": ref, "dp": dp}
    if out:
        d["out"] = out
    if excl:
        d["excl"] = excl
    return d


SEDQ = "sed -E 's/\"[^\",]*,[^\"]*\"/Q/g'"            # quoted fields containing a comma -> Q
SEDK = "sed -E ':a;s/\"([0-9]+),([0-9]{3})/\"\\1\\2/;ta' | sed 's/\"//g'"  # thousands separators out


def cond_str(h, conds):
    out = []
    for name, op, val in conds:
        v = val if isinstance(val, (int, float)) else '"%s"' % val
        out.append("$%d%s%s" % (ci(h, name), op, v))
    return " && ".join(out)


def awk_count(path, h, conds, F=",", skip=1, clean=None):
    prog = "awk -F'%s' 'NR>%d && NF && %s{n++} END{print n+0}'" % (F, skip, cond_str(h, conds))
    if clean:
        return "cat %s | %s | %s" % (path, clean, prog)
    return "%s %s" % (prog, path)


def awk_sum(path, h, col, conds=(), F=",", skip=1, dp=2, clean=None, by=None):
    cond = (" && " + cond_str(h, conds)) if conds else ""
    prog = "awk -F'%s' 'NR>%d && NF%s{s+=$%d} END{printf \"%%.%df\\n\", s}'" % (F, skip, cond, ci(h, col), dp)
    if clean:
        return "cat %s | %s | %s" % (path, clean, prog)
    return "%s %s" % (prog, path)

CLEAN_ALL = SEDK.split(" | ")[0] + " | " + SEDQ + " | sed 's/\"//g'"
