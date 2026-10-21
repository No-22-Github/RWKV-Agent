"""b22f (v2.2: 8-16K long tasks, agent-tool-v3.1, ids 34501-34580) shared writer and helpers."""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch  # noqa: E402

BATCH = Batch(salt="b22f", author="llm:claude-sonnet-b22f", version="v2.2", tool_catalog="agent-tool-v3.1")
META = {}
HAN = re.compile(r"[一-鿿]")
DECOY = {"TR-WEBSTALE": "stale value", "TR-MULTISRC": "the other source's value", "TR-DECOY": "neighbouring item value",
         "TR-SNIPPETVAGUE": "guess from snippet", "TR-TRUNC": "conclusion from the first screen only",
         "TR-LONG": "answer from memory of an unread section", "TR-SUPERSEDE": "the older version's value"}
AXIS = {"TR-WEBSTALE": "VER", "TR-MULTISRC": "CHN", "TR-DECOY": "OBS", "TR-SNIPPETVAGUE": "VER", "TR-TRUNC": "LNG",
        "TR-LONG": "LNG", "TR-SUPERSEDE": "VER"}
_V = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "workbank", "tag-vocab.json")))
TRAP_WORDS = {k: v.get("forbidden_words") or [] for k, v in _V["traps"].items()}


def level_for(n, rc, nfiles, multi):
    if n >= 3 or (multi and n >= 1) or rc >= 8:
        return "L3"
    if n == 2 or (n == 1 and (nfiles >= 3 or rc >= 5)):
        return "L2"
    return "L1"


def is_zh(text):
    return len(HAN.findall(text)) >= 4


def est(text):
    """Tokens in the RWKV World vocabulary, calibrated with `rwkv-lab tokcount` on generated pages:
    Han chars cost about 1.15 token each (not 1.5), other characters about 1 token per 4.9."""
    han = len(HAN.findall(text))
    return int(han * 1.16 + (len(text) - han) / 4.9)


def fx(q, url, title, snippet, content, date, error=None):
    e = {"query_match": q, "url": url, "url_match": re.sub(r"^https?://", "", url).rstrip("/"),
         "title": title, "snippet": snippet, "content": content.rstrip("\n") + "\n", "published_at": date}
    if error:
        e["error"] = error
    return e


def T(p, *, inc=(), any=(), exc=(), req=(), forb=(), review=None, tok=None, maxc=None, anytok=False):
    return dict(p=p, inc=list(inc), any=list(any), exc=list(exc), req=list(req), forb=list(forb),
                review=review, tok=tok, maxc=maxc, anytok=anytok)


def _expect(t):
    e = {}
    if t["req"]:
        e["required_tools"] = t["req"]
    if t["forb"]:
        e["forbidden_tools"] = t["forb"]
    if t["inc"]:
        e["output_contains"] = t["inc"]
        tok = t["tok"]
        if tok is None:
            tok = all(x.isascii() for x in t["inc"]) or any(re.fullmatch(r"[\d.]+", x) for x in t["inc"])
        if tok:
            e["output_contains_token"] = True
    if t["any"]:
        e["output_contains_any"] = t["any"]
        if t["anytok"]:
            e["output_contains_any_token"] = True
    e["output_excludes"] = ["UNKNOWN"] + t["exc"]
    if t["maxc"]:
        e["max_output_chars"] = t["maxc"]
    return e


def _case_expect(efiles, rules, max_calls):
    if rules is None and not max_calls:
        return None
    e = {}
    if rules is not None:
        e["files"] = efiles
    if max_calls:
        e["max_calls"] = max_calls
    return e


def mk(cid, *, sub, tt, desc, turns, steps, why, est_tokens, files=None, web=None, rules=None, must=(), never=(),
       traps=("TR-TRUNC",), ref_calls=5, level=None, notes_extra="", max_calls=None, derived=()):
    """rules: {path: [contains...]} for files the task must write (other fixture files stay unchanged)."""
    files = files or {}
    web = web or []
    corpus = " ".join(files.values()) + " " + " ".join(w["content"] + " " + w["snippet"] for w in web)
    corpus += " " + " ".join(t["p"] for t in turns)
    efiles = {}
    if rules is not None:
        for p in files:
            if p not in rules:
                efiles[p] = {"unchanged": True}
        for p, r in rules.items():
            efiles[p] = {"contains": list(r)}
    derived = list(derived)
    for t in turns:
        for x in t["inc"]:
            assert x in corpus or x in derived, (cid, x)
    for r in (rules or {}).values():
        for x in r:
            assert x in corpus or x in derived, (cid, x)
    for p in [t["p"] for t in turns]:
        assert not re.search(r"测试|判据|verify|benchmark", p.lower()), (cid, p)
        for tool in ("read_file", "web_fetch", "web_search", "search_text", "read_lines", "write_file"):
            assert tool not in p, (cid, tool)
    level = level_for(len(traps), ref_calls, len(files), len(turns) > 1)
    for p in [t["p"] for t in turns]:
        for trap in traps:
            for w in TRAP_WORDS[trap]:
                assert w.lower() not in p.lower(), (cid, trap, w)
    digest = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    wdigest = hashlib.sha256(json.dumps(web, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    v = ("import hashlib, json\ncase = json.load(open(\"case.json\"))\n"
         "assert hashlib.sha256(json.dumps(case[\"files\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest() == %r, \"fixture changed\"\n"
         "assert hashlib.sha256(json.dumps(case[\"web_fixture\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest() == %r, \"web fixture changed\"\n"
         "corpus = \" \".join(case[\"files\"].values()) + \" \".join(w[\"content\"] + \" \" + w[\"snippet\"] for w in case[\"web_fixture\"]) + \" \".join(t[\"prompt\"] for t in case[\"turns\"])\n"
         "need = [x for t in case[\"turns\"] for x in t[\"expect\"].get(\"output_contains\", [])]\n"
         "need += [x for r in case.get(\"expect\", {}).get(\"files\", {}).values() for x in r.get(\"contains\", [])]\n"
         "DERIVED = %s\n"
         "need = [x for x in need if x not in DERIVED]\n"
         "assert all(x in corpus for x in need), need\n"
         "frules = case.get(\"expect\", {}).get(\"files\", {})\n"
         "wrote = {p: \" \".join(r[\"contains\"]) for p, r in frules.items() if r.get(\"contains\")}\n"
         "first = [x for x in case[\"turns\"][0][\"expect\"].get(\"output_contains\", [])]\n"
         "anys = [x for t in case[\"turns\"] for x in t[\"expect\"].get(\"output_contains_any\", [])]\n"
         "res = {\"files\": wrote} if wrote and not first else ({\"expected_string\": need[0]} if need else {\"expected_contains_any\": anys})\n"
         "print(json.dumps(res, ensure_ascii=False))\n" % (digest, wdigest, json.dumps(derived, ensure_ascii=False)))
    tl = []
    for t in turns:
        d = {"prompt": t["p"], "expect": _expect(t)}
        if t["review"]:
            d["review_before"] = t["review"]
        tl.append(d)
    n_pages = len(web)
    p0 = turns[0]["p"].replace("\n", " ")
    alts = "".join("%d. %s\n" % (i + 1, a) for i, a in enumerate(
        [p0, "麻烦帮我：" + p0, p0 + "（用中文回答）" if is_zh(p0) else p0 + " (keep it organised)", "想请你看看：" + p0, "再确认一下：" + p0]))
    notes = ("## Traps\n%s\n\n## Reference solution\n%s\n\n## Why the answer is unique\n%s\n\n## Estimated trajectory tokens\n%d\n"
             "(fixture: %s)\n%s\n\n## Five alternative phrasings of the task\n%s" % (", ".join(traps) or "none", steps.strip("\n"), why.strip("\n"), est_tokens,
                                    ", ".join("%s=%d" % (w["url_match"], est(w["content"])) for w in web) +
                                    ", ".join("%s=%d" % (p, est(c)) for p, c in files.items() if len(c) > 3000), notes_extra, alts))
    BATCH.write_case(cid, desc=desc, task_type=tt, family="b22f-%s-%s" % (sub, cid.split("-")[1]), level=level,
                     ref_calls=ref_calls, files=files, turns=tl, verify=v, notes=notes, traps=list(traps),
                     decoys={t: DECOY[t] for t in traps}, axes=list(dict.fromkeys(["OBS"] + [AXIS[t] for t in traps])),
                     answer_style="natural", web=web, tool_policy={"must_offer": list(must), "never_offer": list(never)},
                     case_expect=_case_expect(efiles, rules, max_calls),
                     extra_tags={"batch": "b22f", "subtype": sub})
    META[cid] = {"sub": sub, "zh": is_zh(" ".join(t["p"] for t in turns)), "turns": len(turns), "est": est_tokens,
                 "plen": sum(len(t["p"]) for t in turns), "pages": n_pages, "prompt_zh": is_zh(turns[0]["p"])}
