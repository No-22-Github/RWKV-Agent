"""b23b (v2.3: entity name in the prompt, but the data is local -> look locally first) shared helpers."""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch  # noqa: E402

BATCH = Batch(salt="b23b", author="llm:claude-sonnet-b23b", version="v2.3", tool_catalog="agent-tool-v3.2")
META = {}
DECOY = {"TR-WEBSTALE": "the web page's different value", "TR-DECOY": "neighbouring item value",
         "TR-FETCHFAIL": "invented page content", "TR-ABSENT": "invented value"}
AXIS = {"TR-WEBSTALE": ["VER"], "TR-DECOY": ["OBS", "VER"], "TR-FETCHFAIL": ["ERR", "VER"], "TR-ABSENT": ["DEC"]}
WEBT = ["web_search", "web_fetch"]
POLICY = {"must_offer": ["list_files", "read_file", "search_text", "web_search", "web_fetch"]}


def _caps(ws):
    out = []
    for w in ws:
        out += [w, w.capitalize()]
        if "'" in w:
            out += [w.replace("'", "’"), w.capitalize().replace("'", "’")]
    return list(dict.fromkeys(out))


# B2: the reply admits the value comes from a local copy / may be stale
CAVEAT = _caps(["本地", "文件", "副本", "存档", "保存", "旧", "过期", "最新", "截至", "笔记", "记录", "当时", "local", "file", "copy", "saved",
                "archive", "outdated", "out of date", "latest", "as of", "older", "stored", "your notes", "record"])
# B2: honest "could not find it"
NOTFOUND = _caps(["没找到", "没有找到", "找不到", "查不到", "未找到", "没查到", "没有查到", "无法确认", "无法找到", "无法获取", "没有相关", "没有记录",
                  "无法核实", "没能找到", "未能找到", "没法确认", "无法得知", "没有这个信息", "没有这方面", "没有可用",
                  "couldn't find", "could not find", "can't find", "cannot find", "didn't find", "did not find", "not find",
                  "unable to find", "unable to confirm", "can't confirm", "cannot confirm", "couldn't confirm", "no record",
                  "no results", "not available", "no information", "not found", "wasn't able", "don't have", "do not have",
                  "no mention", "isn't mentioned", "not mentioned", "unable to verify", "couldn't verify", "no data"])


def is_zh(text):
    return len(re.findall(r"[一-鿿]", text)) >= 4


def fx(key, url, title, snippet, content, date, error=None):
    e = {"query_match": key, "url": url, "url_match": re.sub(r"^https?://", "", url).rstrip("/").lower(), "title": title,
         "snippet": snippet, "content": content.rstrip("\n") + "\n", "published_at": date}
    if error:
        e["error"] = error
    return e


def T(prompt, *, req=(), inc=(), any=(), exc=(), forb=()):
    return dict(prompt=prompt, req=list(req), inc=list(inc), any=list(any), exc=list(exc), forb=list(forb))


def L(prompt, inc, exc=()):
    """A turn that must be answered from the workspace: web tools forbidden."""
    return T(prompt, inc=inc, exc=exc, forb=WEBT)


def W(prompt, inc, exc=(), req=("web_search",)):
    """A turn that needs the web."""
    return T(prompt, req=req, inc=inc, exc=exc)


def _expect(t):
    e = {}
    if t["req"]:
        e["required_tools"] = t["req"]
    if t["forb"]:
        e["forbidden_tools"] = t["forb"]
    if t["inc"]:
        e["output_contains"] = t["inc"]
        if all(x.isascii() for x in t["inc"]) or any(re.fullmatch(r"[\d.]+", x) for x in t["inc"]):
            e["output_contains_token"] = True
    if t["any"]:
        e["output_contains_any"] = t["any"]
    if t["exc"]:
        e["output_excludes"] = t["exc"]
    return e


def mk(cid, *, sub, n, tt, desc, web, turns, files, trap, ref, why, notes_extra, ref_calls, max_calls=None):
    multi = len(turns) > 1
    level = "L2" if ref_calls >= 5 else "L1"
    tt = {"cfg": "read_effective", "doc": "policy_lookup", "hyb": "local_first"}.get(cid.split("-")[0], tt)
    prompts = " ".join(t["prompt"] for t in turns)
    flat = " ".join(w["content"] + " " + w["snippet"] for w in web) + " " + " ".join(files.values()) + " " + prompts
    for t in turns:
        for x in t["inc"]:
            assert len(x) > 1 or x.isdigit(), (cid, x)
            assert x in flat, (cid, x)
        for x in t["exc"]:
            assert x not in " ".join(t["inc"]), (cid, x)
    for p in files:
        assert ".example" not in p
    for w in web:
        assert ".example" not in w["url"], (cid, w["url"])
    assert ".example" not in flat, cid
    srcs = [x for t in turns for x in t["inc"]]
    anyset = list(dict.fromkeys(w for t in turns for w in t["any"]))
    d = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    v = ("import hashlib, json\n"
         "case = json.load(open(\"case.json\"))\n"
         "_pin = hashlib.sha256(json.dumps(case[\"files\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
         "assert _pin == %r, \"fixture changed\"\n"
         "text = \" \".join(w[\"content\"] + \" \" + w[\"snippet\"] for w in case[\"web_fixture\"]) + \" \" + \" \".join(case[\"files\"].values())\n"
         "prompts = \" \".join(t[\"prompt\"] for t in case[\"turns\"])\n"
         "for turn in case[\"turns\"]:\n"
         "    for item in turn[\"expect\"].get(\"output_contains\", []):\n"
         "        assert item in text or item in prompts, item\n" % d)
    if srcs:
        v += "print(json.dumps({\"expected_string\": %s}, ensure_ascii=False))\n" % json.dumps(srcs[0], ensure_ascii=False)
    else:
        v += "print(json.dumps({\"expected_contains_any\": %s}, ensure_ascii=False))\n" % json.dumps(anyset, ensure_ascii=False)
    tl = [{"prompt": t["prompt"], "expect": _expect(t)} for t in turns]
    p0 = turns[0]["prompt"].replace("\n", " ")
    notes = "## Traps\n- %s\n" % trap + "".join("- %s\n" % x for x in notes_extra)
    notes += "\n## Reference solution\n" + ref.strip("\n") + "\n\n## Why the answer is unique\n" + why.strip("\n") + "\n"
    notes += "\nExpected: " + " | ".join(srcs) + "\n"
    alts = [p0, "想确认一下：" + p0, p0 + "（简单说就行）", "Quick question: " + p0, "再问一件事：" + p0]
    notes += "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, a) for i, a in enumerate(alts))
    expect = {"max_calls": max_calls} if max_calls else None
    BATCH.write_case(cid, desc=desc, task_type=tt, family="b23b-%s-%03d" % (sub, n), level=level, ref_calls=ref_calls,
                     files=files, turns=tl, verify=v, notes=notes, traps=[trap], decoys={trap: DECOY[trap]}, axes=AXIS[trap],
                     answer_style="natural", web=web, tool_policy=POLICY, case_expect=expect,
                     extra_tags={"batch": "b23b", "subtype": sub})
    META[cid] = {"sub": sub, "zh": is_zh(prompts), "turns": len(turns), "level": level, "chars": len(turns[0]["prompt"]),
                 "scen": cid.split("-")[0]}


_N = {"B1": 0, "B2": 0, "B0": 0}


def b1(cid, tt, p, files, inc, web=(), exc=(), t2=None, trap=None, decoy_note=""):
    """B1: prompt names a company/product, but the question is about OUR data in the workspace.
    web: same-name page with a different value (exc = that value). t2: ('L'|'W', prompt, inc[, exc])."""
    _N["B1"] += 1
    web = list(web)
    turns = [L(p, inc, exc)]
    if t2:
        k, p2, i2 = t2[:3]
        x2 = t2[3] if len(t2) > 3 else ()
        turns.append(L(p2, i2, x2) if k == "L" else W(p2, i2, x2))
    trap = trap or ("TR-WEBSTALE" if web else "TR-DECOY")
    mk(cid, sub="B1", n=_N["B1"], tt=tt, desc="Prompt names an outside company/product but asks about the user's own data in the workspace; look locally first",
       web=web, turns=turns, files=files, trap=trap,
       ref="list_files/search_text 定位文件 -> read_file 读出值 -> 作答（不上网）" + ("；第二轮" + ("再读本地文件" if t2[0] == "L" else "追问公开信息才 web_search") if t2 else ""),
       why="The workspace file states the value; " + ("the same-name web page deliberately carries a different one." if web else "neighbouring rows carry other values."),
       notes_extra=["对照 B0：同一实体问『公开的现行信息』才该上网。"] + ([decoy_note] if decoy_note else []),
       ref_calls=5 if t2 else 3)


def b0(cid, tt, p, files, web, inc, exc=(), t2=None, any=()):
    """B0 control: same style of prompt, but the question is about public, changing information."""
    _N["B0"] += 1
    turns = [T(p, req=["web_search"], inc=inc, exc=exc, any=any)]
    if t2:
        turns.append(L(t2[0], t2[1], t2[2] if len(t2) > 2 else ()))
    mk(cid, sub="B0", n=_N["B0"], tt=tt, desc="Control: prompt names an outside company/product and asks for its public, current information; go online",
       web=list(web), turns=turns, files=files, trap="TR-WEBSTALE" if exc else "TR-ABSENT",
       ref="web_search -> 必要时 web_fetch -> 作答并说明来源是网页" + ("；第二轮改问我们自己的约定，读本地文件，不再上网" if t2 else ""),
       why="Only the web page states the current public value; the workspace holds nothing, or a stale value.",
       notes_extra=["对照 B1：同一实体问『我们自己的约定』才该读本地。"], ref_calls=4 if t2 else 2)


def b2(cid, tt, p, files, web, *, inc=(), any=(), req=("web_search",), t2=None, trap="TR-FETCHFAIL"):
    """B2: the web gives nothing (empty search / unreachable page). inc+CAVEAT: a local copy exists; any=NOTFOUND: nothing anywhere."""
    _N["B2"] += 1
    turns = [T(p, req=req, inc=inc, any=any)]
    if t2:
        turns.append(L(t2[0], t2[1]))
    mk(cid, sub="B2", n=_N["B2"], tt=tt, desc="Web search comes back empty or the page cannot be opened; %s" % ("a local saved copy exists" if inc else "nothing local either, say so"),
       web=list(web), turns=turns, files=files, trap=trap,
       ref="web_search/web_fetch 失败（至多 2 次）-> " + ("search_text/read_file 找本地副本 -> 作答并说明来自本地、可能不是最新" if inc else "查本地也没有 -> 如实说查不到，不编"),
       why="The web fixture is empty or errors; " + ("the saved local copy is the only source." if inc else "no source anywhere holds the value."),
       notes_extra=["网页拿不到后，不能编造当前值；有本地副本要说明来源。"], ref_calls=4 if t2 else 3,
       max_calls={"web_search": 2, "web_fetch": 2})
