#!/usr/bin/env python3
"""Think-quality analysis for the 2026-10-10 think-full bench (read-only).

Usage: python3 -I analyze_think.py <command>
  stats            print aggregate tables
  sample CLASS N   print N random steps of a rule class (for manual review)
  case RUN CASE    print the full think/action trace of one case
"""
import glob
import json
import os
import random
import re
import sys
import zlib
from collections import Counter, defaultdict

ROOT = "/Users/no22/Projects/RWKV-Agent"
RUNS = ROOT + "/local/runs/bench-20261010-thinkfull"
CASES = ROOT + "/bench/workbank/cases"
HERE = os.path.dirname(os.path.abspath(__file__))

TOOLS = ["append_file", "calculator", "data_query", "datetime", "list_files", "read_file",
         "read_lines", "replace_lines", "search_text", "web_fetch", "web_search", "write_file",
         "no_tool", "remove_files", "bash", "get_weather"]
STOP = set("""the and for that this with from have will your you are not but all can has was were its into
than then them they their what when which while would could should about there here also only just more
some such each other over under been being does did how out any use used using need needs want wants
user asks asked asking answer final reply question tool tools call calls file files let make sure""".split())


def load_case_defs():
    defs = {}
    for f in glob.glob(CASES + "/*/*/case.json"):
        d = json.load(open(f))
        defs[d["id"]] = d
    return defs


def split_think(out, group):
    """Return (think_text, closed, post_text, has_think)."""
    if group == "T":
        body = out[1:] if out.startswith(">") else out
        if "</think>" in body:
            th, post = body.split("</think>", 1)
            return th.strip(), True, post.strip(), True
        return body.strip(), False, "", True
    m = re.search(r"<think>", out)
    if not m:
        return "", False, out.strip(), False
    body = out[m.end():]
    if "</think>" in body:
        th, post = body.split("</think>", 1)
        return th.strip(), True, post.strip(), True
    return body.strip(), False, "", True


def tool_responses(prompt):
    return re.findall(r"<tool_response>(.*?)</tool_response>", prompt, re.S)


def retry_kind(prompt):
    i = prompt.rfind("\n\nUser: ")
    last = prompt[i + 8:i + 120]
    if last.startswith("Your previous reasoning never finished"):
        return "cutoff"
    if last.startswith("Your previous response was invalid"):
        return "invalid"
    if last.startswith("Tool execution is complete"):
        return "forced"
    if last.startswith("Use the Tool results"):
        return "normal"
    if "rejected" in last or "failed" in last:
        return "toolerr"
    return "first"


def load_run(name, defs):
    group = name[0]
    bench = "workbank" if "workbank" in name else "bfclp"
    s = json.load(open("%s/%s/summary.json" % (RUNS, name)))
    steps = []
    for case in s["cases"]:
        cd = defs.get(case["id"], {})
        files = set(cd.get("files", {}).keys())
        for ti, t in enumerate(case["turns"]):
            sts = t["result"]["steps"]
            for st in sts:
                th, closed, post, has = split_think(st["model_output"], group)
                p = st["request"]["prompt"]
                trs = tool_responses(p)
                steps.append(dict(
                    run=name, group=group, bench=bench, case=case["id"], cat=case["category"],
                    passed=bool(case["passed"]), turn=ti, n=st["number"], nsteps=len(sts),
                    stage=st["stage"], think=th, closed=closed, post=post, has_think=has,
                    out=st["model_output"], atype=st.get("action_type"), tool=st.get("tool"),
                    args=st.get("tool_arguments"), tool_ok=(st.get("tool_result") or {}).get("ok"),
                    rej=st.get("tool_rejected_reason"), perr=st.get("protocol_error"),
                    retry=retry_kind(p), results=trs, files=files,
                    task=" ".join(x["prompt"] for x in case["turns"][:ti + 1]),
                    fails=t.get("failures") or [], forced=t["result"].get("forced_answer_reason"),
                    final=t["result"].get("output", ""), expect=(cd.get("turns", [{}])[ti].get("expect", {})
                                                                  if ti < len(cd.get("turns", [])) else {}),
                ))
    return steps


# ---------------------------------------------------------------- features
ENT_RE = re.compile(r"[A-Za-z0-9_]+(?:[-./:][A-Za-z0-9_]+)+|[A-Za-z]+_[A-Za-z0-9_]+|\b\d[\d,]*\.?\d*\b")
NUM_RE = re.compile(r"\b\d[\d,]*\.?\d*\b")
RULE_RE = re.compile(r"Never mix|exactly one|tool_call envelope|only the final answer|ordinary text|"
                     r"Decide with the evidence|Never invent|Never invoke tools|without an envelope|"
                     r"Markdown fence|role label|local-first|untrusted data|available tools (are|include)|"
                     r"tools? available|If new tool evidence|If you cannot determine", re.I)
REFLECT_RE = re.compile(r"(search|result|results|file|call|tool|output|data|query|read|list|response|log|content|entries)"
                        r"[^.\n]{0,60}\b(shows?|showed|returned|failed|fails|contains?|empty|not a directory|error|"
                        r"does not|did not|doesn't|didn't|reveals?|lists?|includes?|indicates?|confirms?|no such|"
                        r"zero|rejected|found|matches)\b", re.I)
RATIONALE_RE = re.compile(r"\b(to find|to check|to see|to determine|to locate|to identify|because|since|so that|"
                          r"in order to|instead|first|then|next|rather than|to verify|to count|to compute|"
                          r"to calculate|need to find|is needed|which would|which will)\b", re.I)
INTENT_RE = re.compile(r"\b(I (need|should|will|can|must|'ll)|let me|let's|I'll|we need|we should|we can)\b", re.I)
CALC_RE = re.compile(r"(\d\s*[-+*/x×]\s*\d|=\s*\d|\bsum\b|\btotal\b|\bsort|\bcount\b|\bmax\b|\bmin\b|\baverage|\bcompar|\bdifference|\bequals?\b)", re.I)
CLAIM_ANS_RE = re.compile(r"(answer|outcome|result|value|port|total|count|number|path|timestamp)\s+(is|=|should be|would be)\s*[:\"“']?\s*([^\n.\"”']{1,60})", re.I)


THINK_FAIL_RE = re.compile(r"(returned no|no results|not found|does(n't| not) exist|did not (return|find)|failed|"
                           r"is empty|was empty|are empty|not a directory|no such|404|rejected|invalid)", re.I)
VAGUE_RE = re.compile(r"(explore|understand|get a (sense|picture)|look at the (files|workspace)|"
                      r"start (by|with)|break (this|it) down|let me think)", re.I)
NOTOOL_RE = re.compile(r"(no|any|without a|don't have a|do not have a) (tool|access)[^.\n]{0,50}(look|read|query|count|fetch|open|"
                       r"search|access|compute|determine)|(cannot|can't|unable to) (access|read|look up|query|open)", re.I)


def words(t):
    return {w for w in re.findall(r"[a-z]{4,}", t.lower()) if w not in STOP}


def ents(t):
    out = set()
    for e in ENT_RE.findall(t):
        e = e.strip(".,:/-").lower()
        if e in TOOLS or e in ("tool_call", "tool_response", "no_tool") or len(e) < 2:
            continue
        if NUM_RE.fullmatch(e) and len(e.replace(",", "").replace(".", "")) < 2:
            continue
        out.add(e)
    return out


def sentences(t):
    ss = re.split(r"(?<=[.!?])\s+|\n+", t)
    return [s.strip() for s in ss if len(s.strip()) > 3]


def repetition(t):
    """Return (dup_sentence_share, zlib_ratio)."""
    ss = sentences(t)
    dup = 0.0
    if len(ss) >= 3:
        c = Counter(s.lower() for s in ss)
        dup = sum(v - 1 for v in c.values()) / len(ss)
    zr = len(zlib.compress(t.encode())) / max(1, len(t.encode())) if len(t) > 400 else 1.0
    return dup, zr


def features(r):
    th = r["think"]
    f = {}
    f["len"] = len(th)
    f["dup"], f["zr"] = repetition(th)
    task_e = ents(r["task"])
    res_txt = "\n".join(r["results"])
    res_e = ents(res_txt) - task_e
    th_e = ents(th)
    f["ev_use"] = sorted(th_e & res_e)
    f["task_ent"] = sorted(th_e & task_e)
    f["derived"] = sorted(e for e in th_e if NUM_RE.fullmatch(e) and e not in task_e and e not in ents(res_txt))
    f["has_prior"] = bool(r["results"])
    f["reflect"] = bool(REFLECT_RE.search(th)) and f["has_prior"]
    last = r["results"][-1] if r["results"] else ""
    f["last_fail"] = bool(re.search(r'"ok":\s*false|"results":\s*\[\]|no such file|not found|rejected|error', last, re.I))
    f["calc"] = bool(CALC_RE.search(th)) and (len(th_e) >= 2)
    f["rationale"] = bool(RATIONALE_RE.search(th))
    f["intent"] = bool(INTENT_RE.search(th))
    f["tool_named"] = sorted({t for t in TOOLS if re.search(r"\b%s\b" % t, th)})
    f["path_named"] = bool(re.search(r"[\w-]+\.(csv|txt|md|py|log|yml|yaml|json|ini|conf)\b|\w+/\w+", th))
    tw = words(r["task"]) | words("never mix commentary tool call exactly envelope markdown role label")
    ss = sentences(th)
    rs = 0
    for s in ss:
        w = words(s)
        if not w:
            continue
        if RULE_RE.search(s) or len(w & tw) / len(w) >= 0.75:
            if not (ents(s) & (res_e | set(f["derived"]))):
                rs += 1
    f["restate"] = rs / max(1, len(ss))
    f["rule_hits"] = len(RULE_RE.findall(th))
    f["leak_call"] = "<tool_call" in th
    f["notool_claim"] = bool(NOTOOL_RE.search(th))
    return f


def classify(r, f):
    """Primary class for one step's think. Order matters."""
    if not r["has_think"]:
        return "no_think"
    if not r["think"]:
        return "empty"
    if f["len"] > 600 and (f["dup"] >= 0.35 or f["zr"] < 0.12):
        return "degenerate"
    if re.search(r"(.)\1{12,}|(\b\w+\b)(\s+\2){8,}", r["think"]):
        return "degenerate"
    if not r["closed"]:
        if f["leak_call"]:
            return "unclosed_call"
        if f["len"] > 9000:
            return "unclosed_long"
        return "unclosed_other"
    tfail = bool(THINK_FAIL_RE.search(r["think"]))
    val = f["has_prior"] and not tfail and (f["ev_use"] or f["calc"] or f["derived"]) and not f["last_fail"]
    fail = f["has_prior"] and (f["last_fail"] or tfail) and (f["reflect"] or f["ev_use"] or f["calc"])
    if val and f["restate"] < 0.8:
        return "result_value"
    if fail and f["restate"] < 0.8:
        return "result_fail"
    if f["has_prior"] and f["reflect"] and f["restate"] < 0.8:
        return "result_value"
    if f["task_ent"] or f["tool_named"] or f["path_named"] or f["ev_use"]:
        enum = len(re.findall(r"^\s*(\d+[.)]|[-*])\s", r["think"], re.M)) >= 2
        vague = bool(VAGUE_RE.search(r["think"])) and not enum
        if (f["rationale"] or enum) and f["restate"] < 0.7 and not vague:
            return "plan"
        if f["restate"] < 0.5 and not vague and f["path_named"]:
            return "plan"
        if vague:
            return "shallow"
        if f["restate"] >= 0.5 and f["intent"]:
            return "shallow"
    if f["restate"] >= 0.6:
        return "recite"
    if f["rationale"] or f["intent"]:
        return "shallow"
    return "recite"


def annotate(steps):
    for r in steps:
        r["f"] = features(r)
        r["cls"] = classify(r, r["f"])
    return steps


# ---------------------------------------------------------------- behaviour flags
BAD_CLS = ("degenerate", "unclosed_call", "unclosed_other", "unclosed_long", "empty")


def mark_actions(steps):
    """Flag repeated calls and ungrounded targets; steps must be in file order."""
    seen = defaultdict(set)
    for r in steps:
        key = (r["run"], r["case"], r["turn"])
        sig = json.dumps([r["tool"], r["args"]], sort_keys=True) if r["tool"] else None
        r["repeat"] = bool(sig and sig in seen[key])
        if sig:
            seen[key].add(sig)
        r["ungrounded"] = False
        if r["tool"] in ("read_file", "list_files", "read_lines", "search_text", "data_query") and isinstance(r["args"], dict):
            p = r["args"].get("path")
            if isinstance(p, str) and p and p not in (".", ""):
                q = p.lstrip("./")
                known = any(f == q or f.startswith(q.rstrip("/") + "/") for f in r["files"])
                known = known or q in " ".join(r["results"]) or q in r["task"]
                r["ungrounded"] = (not known) or p.startswith("/")
    return steps


def review_sample():
    defs = load_case_defs()
    st = []
    for run in ("T-workbank-k0", "T-workbank-k1"):
        st += annotate(load_run(run, defs))
    mark_actions(st)
    random.seed(20261010)
    closed = [r for r in st if r["cls"] not in BAD_CLS]
    return random.sample(closed, 120), st


def review_sample_A():
    defs = load_case_defs()
    st = []
    for run in ("A-workbank-k0", "A-workbank-k1"):
        st += annotate(load_run(run, defs))
    pool = [r for r in st if r["has_think"] and r["closed"] and r["cls"] not in BAD_CLS]
    random.seed(8)
    return random.sample(pool, 24)


def fisher_p(a, b, c, d):
    """Two-sided Fisher exact p for [[a,b],[c,d]] (stdlib only)."""
    from math import comb
    n1, n2, k = a + b, c + d, a + c
    tot = comb(n1 + n2, k)

    def pr(x):
        return comb(n1, x) * comb(n2, k - x) / tot
    p0 = pr(a)
    return sum(pr(x) for x in range(max(0, k - n2), min(n1, k) + 1) if pr(x) <= p0 + 1e-12)


def pct(a, b):
    return "%d/%d (%.0f%%)" % (a, b, 100.0 * a / b) if b else "0/0"


# ---------------------------------------------------------------- stats
def load_all(names):
    defs = load_case_defs()
    out = {}
    for n in names:
        out[n] = mark_actions(annotate(load_run(n, defs)))
    return out


def dist(steps, title):
    c = Counter(r["cls"] for r in steps)
    n = len(steps)
    print("\n## %s  (steps=%d)" % (title, n))
    for k, v in c.most_common():
        print("  %-14s %s" % (k, pct(v, n)))


def section_class_dist(D):
    for name in D:
        dist(D[name], name)
    # rule stratum -> manual label confusion, and stratified estimate
    import manual_labels as ml
    samp, st = review_sample()
    conf = defaultdict(Counter)
    flags = Counter()
    for i, r in enumerate(samp):
        lab = ml.LABELS[i].split("+")
        conf[r["cls"]][lab[0]] += 1
        for f in lab[1:]:
            flags[f] += 1
    print("\n## rule class x manual label (n=120 closed, non-degenerate T-workbank steps)")
    for k, v in conf.items():
        print("  %-13s n=%-3d %s" % (k, sum(v.values()), dict(v)))
    strata = Counter(r["cls"] for r in st if r["cls"] not in BAD_CLS)
    est = Counter()
    for k, n in strata.items():
        tot = sum(conf[k].values())
        for lab, v in conf[k].items():
            est[lab] += n * v / tot
    tot = sum(est.values())
    print("  stratified estimate of manual class over %d closed steps: %s" %
          (tot, {k: "%.0f (%.0f%%)" % (v, 100 * v / tot) for k, v in est.most_common()}))
    print("  manual flags in sample:", dict(flags), "of 120")
    # rule precision of repeat flag vs manual X on the sample
    xs = [(r["repeat"], "X" in ml.LABELS[i]) for i, r in enumerate(samp)]
    tp = sum(1 for a, b in xs if a and b)
    print("  repeat-flag vs manual X: both=%d rule_only=%d manual_only=%d" %
          (tp, sum(1 for a, b in xs if a and not b), sum(1 for a, b in xs if b and not a)))


def case_table(steps):
    """Per case-run aggregates."""
    by = defaultdict(list)
    for r in steps:
        by[(r["run"], r["case"])].append(r)
    rows = []
    for k, rs in by.items():
        n = len(rs)
        th = [r for r in rs if r["has_think"]]
        rows.append(dict(
            key=k, passed=rs[0]["passed"], n=n,
            res=sum(r["cls"] in ("result_value", "result_fail") for r in rs) / n,
            val=sum(r["cls"] == "result_value" for r in rs) / n,
            bad=sum(r["cls"] in BAD_CLS for r in rs) / n,
            deg=any(r["cls"] == "degenerate" for r in rs),
            medlen=sorted(len(r["think"]) for r in rs)[n // 2],
            ev=sum(bool(r["f"]["ev_use"]) for r in rs if r["n"] > 1) / max(1, sum(1 for r in rs if r["n"] > 1)),
            rep=sum(r["repeat"] for r in rs) / n,
        ))
    return rows


def section_pass_vs_fail(D):
    allT = [r for n in D if n.startswith("T-workbank") for r in D[n]]
    rows = case_table(allT)
    P = [x for x in rows if x["passed"]]
    F = [x for x in rows if not x["passed"]]
    print("\n## pass vs fail (T workbank case-runs: pass=%d fail=%d)" % (len(P), len(F)))
    for key in ("n", "res", "val", "bad", "medlen", "ev", "rep"):
        mp = sum(x[key] for x in P) / len(P)
        mf = sum(x[key] for x in F) / len(F)
        print("  %-7s pass=%.2f fail=%.2f" % (key, mp, mf))
    print("  any degenerate step: pass %s  fail %s" % (pct(sum(x["deg"] for x in P), len(P)), pct(sum(x["deg"] for x in F), len(F))))
    # by task category
    cats = defaultdict(lambda: [0, 0])
    for n in D:
        if n.startswith("T-workbank"):
            seen = set()
            for r in D[n]:
                if (n, r["case"]) in seen:
                    continue
                seen.add((n, r["case"]))
                cats[r["cat"]][0] += r["passed"]
                cats[r["cat"]][1] += 1
    print("  T pass by category:", {k: "%d/%d" % tuple(v) for k, v in sorted(cats.items())})


def section_use_prev(D):
    print("\n## multi-step: does think use the previous tool result? (normal-retry steps, n>=2 with prior results)")
    for grp in ("T", "A"):
        rs = [r for n in D if n.startswith(grp + "-workbank") for r in D[n]
              if r["retry"] in ("normal", "toolerr") and r["has_think"] and r["results"] and r["think"]]
        n = len(rs)
        ev = sum(bool(r["f"]["ev_use"]) for r in rs)
        refl = sum(r["f"]["reflect"] for r in rs)
        scratch = sum(1 for r in rs if re.match(r"(The user|We need|I need to)", r["think"]) and not r["f"]["reflect"]
                      and not r["f"]["ev_use"])
        both = sum(1 for r in rs if r["f"]["restate"] >= 0.6)
        print("  %s: steps=%d  cite new value/entity from results=%s  reflect-on-result wording=%s  "
              "start-from-scratch (no reference)=%s  mostly-restatement=%s" %
              (grp, n, pct(ev, n), pct(refl, n), pct(scratch, n), pct(both, n)))
    # first-step vs later
    for grp in ("T",):
        rs = [r for n in D if n.startswith(grp + "-workbank") for r in D[n] if r["retry"] == "first"]
        print("  %s first-step think count=%d, classes=%s" % (grp, len(rs), dict(Counter(r["cls"] for r in rs))))


def section_ab(D):
    print("\n## A vs T think quality (workbank, steps that contain a think)")
    for grp in ("A", "T"):
        rs = [r for n in D if n.startswith(grp + "-workbank") for r in D[n]]
        th = [r for r in rs if r["has_think"]]
        L = sorted(len(r["think"]) for r in th)
        print("  %s: steps=%d with_think=%s median_len=%d p90=%d closed=%s degenerate=%s unclosed_call=%s "
              "ungrounded_path=%s repeat_call=%s" % (
                  grp, len(rs), pct(len(th), len(rs)), L[len(L) // 2], L[int(len(L) * .9)],
                  pct(sum(r["closed"] for r in th), len(th)),
                  pct(sum(r["cls"] == "degenerate" for r in th), len(th)),
                  pct(sum(r["cls"] == "unclosed_call" for r in th), len(th)),
                  pct(sum(r["ungrounded"] for r in rs if r["tool"]), sum(1 for r in rs if r["tool"])),
                  pct(sum(r["repeat"] for r in rs if r["tool"]), sum(1 for r in rs if r["tool"]))))
        print("     classes:", dict(Counter(r["cls"] for r in th)))
    # A: steps with vs without think -> action quality
    rs = [r for n in D if n.startswith("A-workbank") for r in D[n] if r["retry"] in ("first", "normal")]
    for flag in (True, False):
        xs = [r for r in rs if r["has_think"] == flag]
        print("  A steps with_think=%s: n=%d protocol_error=%s tool_err=%s ungrounded=%s" % (
            flag, len(xs), pct(sum(bool(r["perr"]) for r in xs), len(xs)),
            pct(sum(r["tool_ok"] is False for r in xs if r["tool"]), sum(1 for r in xs if r["tool"])),
            pct(sum(r["ungrounded"] for r in xs if r["tool"]), sum(1 for r in xs if r["tool"]))))
    # A cases with any think vs none: pass
    for grp in ("A",):
        pass


def section_pass_excl_notool(D):
    allT = [r for n in D if n.startswith("T-workbank") for r in D[n]]
    rows = [x for x in case_table(allT)]
    cat = {(r["run"], r["case"]): r["cat"] for r in allT}
    sub = [x for x in rows if cat[x["key"]] != "notool"]
    P = [x for x in sub if x["passed"]]
    F = [x for x in sub if not x["passed"]]
    print("\n## pass vs fail excluding notool category (pass=%d fail=%d)" % (len(P), len(F)))
    for key in ("n", "res", "val", "bad", "medlen", "ev", "rep"):
        print("  %-7s pass=%.2f fail=%.2f" % (key, sum(x[key] for x in P) / max(1, len(P)), sum(x[key] for x in F) / len(F)))
    for key, fn in (("any degenerate", lambda x: x["deg"]), ("ev>0", lambda x: x["ev"] > 0),
                    ("repeat>0", lambda x: x["rep"] > 0)):
        a1, b1 = sum(fn(x) for x in P), len(P) - sum(fn(x) for x in P)
        c1, d1 = sum(fn(x) for x in F), len(F) - sum(fn(x) for x in F)
        print("  %-15s pass %s  fail %s  fisher p=%.3f" % (key, pct(a1, len(P)), pct(c1, len(F)), fisher_p(a1, b1, c1, d1)))
    # notool-only view
    sub2 = [x for x in rows if cat[x["key"]] == "notool"]
    print("  notool case-runs: pass %d / %d" % (sum(x["passed"] for x in sub2), len(sub2)))


def section_wins_and_rit(D):
    import manual_labels as ml
    print("\n## T-over-A wins (manual verdict)")
    c = Counter(ml.WINS.values())
    print("  ", dict(c), "of", len(ml.WINS), "(C think causal, F format/contract luck, L lucky abstention)")
    n_fail = sum(1 for n in D if n.startswith("T-workbank") for cs in
                 {(r["case"]) for r in D[n] if not r["passed"]})
    print("\n## right answer in think but case failed (manual verification of string-match hits)")
    tot = 0
    for k, v in ml.RIGHT_IN_THINK.items():
        tot += len(v)
        print("  %s: %d" % (k, len(v)))
    print("  total genuine = %d of %d failed T case-runs" % (tot, n_fail))
    allT = [r for n in D if n.startswith("T-workbank") for r in D[n]]
    hits, by = right_in_think(allT)
    print("  auto string-match flagged:", len(hits))


def section_manual_AT(D):
    import manual_labels as ml
    samp, st = review_sample()
    first = [(i, r) for i, r in enumerate(samp) if r["n"] == 1]
    later = [(i, r) for i, r in enumerate(samp) if r["n"] > 1]
    def dd(items, labs):
        c = Counter(labs[i].split("+")[0] for i, _ in items)
        n = len(items)
        return "n=%d " % n + " ".join("%s=%d(%.0f%%)" % (k, v, 100 * v / n) for k, v in sorted(c.items()))
    print("\n## manual labels: T first-step vs later steps vs A (all A thinks are mostly first-step)")
    print("  T first-step :", dd(first, ml.LABELS))
    print("  T later steps:", dd(later, ml.LABELS))
    A = review_sample_A()
    print("  A (closed think, n=24):", dd(list(enumerate(A)), ml.A_LABELS))
    fl = lambda labs, items: sum(1 for i, _ in items for f in labs[i].split("+")[1:] if f == "W")
    print("  W (fact/tool error) flags: T first=%d/%d  T later=%d/%d  A=%d/24" % (
        fl(ml.LABELS, first), len(first), fl(ml.LABELS, later), len(later), fl(ml.A_LABELS, list(enumerate(A)))))
    xs = lambda labs, items: sum(1 for i, _ in items if "X" in labs[i].split("+")[1:])
    print("  X (think != action) flags: T first=%d/%d  T later=%d/%d  A=%d/24" % (
        xs(ml.LABELS, first), len(first), xs(ml.LABELS, later), len(later), xs(ml.A_LABELS, list(enumerate(A)))))
    for g in ("T", "A"):
        rs = [r for n in D if n.startswith(g + "-workbank") for r in D[n] if r["n"] == 1 and r["has_think"]]
        print("  %s first-step think states 'no tool / cannot access' claim: %s" % (
            g, pct(sum(r["f"]["notool_claim"] for r in rs), len(rs))))


def section_first_step(D):
    print("\n## first-step think, A vs T (workbank)")
    for grp in ("A", "T"):
        rs = [r for n in D if n.startswith(grp + "-workbank") for r in D[n] if r["n"] == 1]
        th = [r for r in rs if r["has_think"]]
        print("  %s: first steps=%d with_think=%s closed=%s median_len=%d classes=%s" % (
            grp, len(rs), pct(len(th), len(rs)), pct(sum(r["closed"] for r in th), len(th)),
            sorted(len(r["think"]) for r in th)[len(th) // 2], dict(Counter(r["cls"] for r in th).most_common())))
        later = [r for n in D if n.startswith(grp + "-workbank") for r in D[n]
                 if r["n"] > 1 and r["retry"] in ("normal", "toolerr")]
        print("     later (normal/toolerr) steps=%d with_think=%s" % (len(later), pct(sum(r["has_think"] for r in later), len(later))))
    print("\n## T class by retry kind")
    T = [r for n in D if n.startswith("T-workbank") for r in D[n]]
    for k in ("first", "normal", "toolerr", "cutoff", "forced"):
        xs = [r for r in T if r["retry"] == k]
        print("  %-8s n=%d %s" % (k, len(xs), dict(Counter(r["cls"] for r in xs).most_common())))


def section_fail_buckets_and_cost(D):
    print("\n## heuristic failure buckets (turn level, workbank k0+k1)")
    for g in "TA":
        seen, c = set(), Counter()
        for n in D:
            if n[0] != g or "workbank" not in n:
                continue
            for r in D[n]:
                k = (n, r["case"], r["turn"])
                if k in seen or r["passed"]:
                    continue
                seen.add(k)
                f = " ".join(r["fails"])
                if "violated the answer contract" in r["final"]:
                    b = "contract-violated stub"
                elif "protocol error" in f:
                    b = "protocol error (unclosed think / JSON)"
                elif r["final"].strip() == "":
                    b = "empty output"
                elif "is not a plain number" in f or ("after answer normalization" in f and r["final"].count(" ") > 3):
                    b = "value wrapped in prose (format)"
                elif "want" in f or "does not contain" in f or "numeric output" in f:
                    b = "wrong value / missing content"
                else:
                    b = "other"
                c[b] += 1
        print("  %s: %d %s" % (g, sum(c.values()), dict(c.most_common())))
    T = [r for n in D if n.startswith("T-workbank") for r in D[n]]
    bad = [r for r in T if r["cls"] in BAD_CLS]
    print("\n## cost of unclosed/looping thinks (T workbank)")
    print("  bad steps %s; chars in bad steps = %.0f%% of all generated chars; cutoff-retry steps=%d (recovered to a valid closed action: %d)" % (
        pct(len(bad), len(T)), 100.0 * sum(len(r["out"]) for r in bad) / sum(len(r["out"]) for r in T),
        sum(r["retry"] == "cutoff" for r in T), sum(1 for r in T if r["retry"] == "cutoff" and r["closed"] and r["atype"] in ("tool", "final", "no_tool"))))
    by = defaultdict(list)
    for r in T:
        by[(r["run"], r["case"])].append(r)
    w = [k for k, rs in by.items() if any(x["cls"] in BAD_CLS for x in rs)]
    wo = [k for k in by if k not in set(w)]
    print("  case-runs with >=1 bad step: %d, pass %s ; without: %d, pass %s" % (
        len(w), pct(sum(by[k][0]["passed"] for k in w), len(w)), len(wo), pct(sum(by[k][0]["passed"] for k in wo), len(wo))))
    calls = Counter()
    for r in T:
        if r["tool"] == "calculator" and isinstance(r["args"], dict) and r["args"].get("expression") == "4500*0.082*30/365":
            calls[r["case"]] += 1
    print("  calculator calls that copy the repair-message example expression verbatim:", dict(calls))
    print("  tool-call repeat rate by think class (T):")
    for c in ("plan", "shallow", "result_value", "result_fail"):
        xs = [r for r in T if r["cls"] == c and r["tool"]]
        print("    %-12s n=%d repeat=%.2f ok=%.2f" % (c, len(xs), sum(r["repeat"] for r in xs) / len(xs), sum(r["tool_ok"] is True for r in xs) / len(xs)))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    sys.path.insert(0, HERE)
    names = [os.path.basename(p) for p in sorted(glob.glob(RUNS + "/[AT]-workbank-k*"))
             if os.path.isdir(p)]
    names += [os.path.basename(p) for p in sorted(glob.glob(RUNS + "/[AT]-bfclp-k*")) if os.path.isdir(p)]
    names = [n for n in names if os.path.exists("%s/%s/summary.json" % (RUNS, n)) and n[-2:] in ("k0", "k1")]
    if cmd == "stats":
        D = load_all(names)
        section_class_dist(D)
        section_pass_vs_fail(D)
        section_use_prev(D)
        section_ab(D)
        section_pass_excl_notool(D)
        section_wins_and_rit(D)
        section_first_step(D)
        section_manual_AT(D)
        section_fail_buckets_and_cost(D)
    elif cmd == "case":
        D = load_all([sys.argv[2]])
        sel = [r for r in D[sys.argv[2]] if r["case"] == sys.argv[3]]
        for r in sel:
            if True:
                print("--- step %d stage=%s retry=%s cls=%s tool=%s args=%s ok=%s rej=%s" % (
                    r["n"], r["stage"], r["retry"], r["cls"], r["tool"], str(r["args"])[:90], r["tool_ok"], r["rej"]))
                if r["results"]:
                    print("   PRIOR:", r["results"][-1][:160].replace("\n", " "))
                print("   THINK:", r["think"][:700].replace("\n", " ⏎ "))
                print("   POST :", r["post"][:200].replace("\n", " ⏎ "))
        print("FINAL:", sel[-1]["final"][:200], "PASSED:", sel[-1]["passed"])



# ---------------------------------------------------------------- right-in-think, wrong-in-action
def expected_strings(exp):
    out = []
    if "expected_number" in exp:
        n = exp["expected_number"]
        out.append([("%g" % n)] if float(n) != int(n) else [str(int(n)), "{:,}".format(int(n))])
    if "output_equals" in exp:
        out.append([exp["output_equals"]])
    if "output_equals_any" in exp:
        out.append(list(exp["output_equals_any"]))
    if "output_contains" in exp:
        out.extend([[x] for x in exp["output_contains"]])
    if "output_contains_any" in exp:
        out.append(list(exp["output_contains_any"]))
    return out


def has_token(text, alts):
    for a in alts:
        pat = r"(?<![\w.])" + re.escape(a) + r"(?![\w])" if re.match(r"^[\d,.]+$", a) else re.escape(a)
        if re.search(pat, text, re.I):
            return True
    return False


def right_in_think(steps):
    """Failed case-runs whose think contains every expected answer fragment at some step."""
    by = defaultdict(list)
    for r in steps:
        by[(r["run"], r["case"])].append(r)
    hits = []
    for k, rs in by.items():
        if rs[0]["passed"]:
            continue
        exp = expected_strings(rs[0]["expect"] or {})
        if not exp:
            continue
        for r in rs:
            if r["has_think"] and r["think"] and all(has_token(r["think"], alts) for alts in exp):
                # skip if the expected token is already in the task text (trivial echo)
                if all(has_token(rs[0]["task"], alts) for alts in exp):
                    continue
                hits.append((k, r))
                break
    return hits, by


if __name__ == "__main__":
    main()
