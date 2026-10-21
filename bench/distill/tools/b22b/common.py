"""b22b (v2.2: user gives a URL -> read the page, web ids 34101-34150) shared helpers."""
import hashlib
import inspect
import json
import os
import re
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch  # noqa: E402

BATCH = Batch(salt="b22b", author="llm:claude-sonnet-b22b", version="v2.2", tool_catalog="agent-tool-v3.1")
META = {}
_VOCAB = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "workbank", "tag-vocab.json")))
TRAP_AXIS = {k: v.get("axis") for k, v in _VOCAB["traps"].items()}
TRAP_WORDS = {k: v.get("forbidden_words") or [] for k, v in _VOCAB["traps"].items()}
TOOLS = _VOCAB["tools"]
DECOY = {"TR-DECOY": "neighbouring item value", "TR-WEBSTALE": "superseded value", "TR-FETCHFAIL": "invented page content",
         "TR-MULTISRC": "web-only or file-only value"}


def _caps(ws):
    out = []
    for w in ws:
        out += [w, w.capitalize()]
        if "'" in w:
            out += [w.replace("'", "’"), w.capitalize().replace("'", "’")]
    return list(dict.fromkeys(out))


NOWEB = _caps([
    "我没有上网", "没有上网", "无法上网", "不能上网", "没有联网", "无法联网", "不能联网", "没法联网", "没有网页工具", "没有浏览网页",
    "无法浏览网页", "无法访问网页", "无法访问网址", "无法访问链接", "没有访问网页", "不能访问网页", "没有访问网络", "无法访问互联网",
    "无法访问外部网站", "没有网络访问", "cannot browse", "can't browse", "no web access", "no internet access",
    "don't have access to the internet", "do not have access to the internet", "don't have internet access", "unable to browse",
    "unable to access the web", "unable to access external", "cannot access external", "can't access external",
    "cannot access the internet", "can't access the internet", "don't have the ability to browse", "no ability to browse"])

_FAIL_ZH = ["打不开", "无法打开", "没能打开", "未能打开", "没法打开", "无法访问", "没法访问", "访问失败", "访问不了", "抓取失败", "获取失败",
            "读取失败", "加载失败", "打开失败", "拉取失败", "无法获取", "没能获取", "未能获取", "没有获取", "没获取到", "获取不到", "取不到",
            "无法读取", "没能读取", "未能读取", "无法加载", "没能加载", "未能成功", "没有成功", "未成功", "没成功", "502", "报错", "出错",
            "错误", "失败", "不可用", "暂时无法", "没拿到", "没有拿到", "没能看到", "无法查看", "没法查看", "没读到", "没有读到", "读不到",
            "无法确认", "没法确认", "无法核实", "没法核实", "无法验证", "没有核实", "未核实", "未能核实", "没能核实", "没能确认", "未能确认",
            "没有返回", "没有内容", "没有正文", "空白", "页面为空", "内容为空", "读取不到", "没能读到", "未能读到", "没法读取", "没法打开页面",
            "不能访问", "无法抓取", "没能抓取", "没抓到", "超时"]
_FAIL_EN = ["couldn't open", "could not open", "can't open", "cannot open", "unable to open", "unable to load", "couldn't load",
            "could not load", "can't load", "cannot load", "couldn't fetch", "could not fetch", "unable to fetch", "failed",
            "failure", "error", "502", "bad gateway", "couldn't access", "could not access", "unable to access", "can't access",
            "cannot access", "unable to retrieve", "couldn't retrieve", "could not retrieve", "unable to read", "couldn't read",
            "could not read", "unavailable", "not available", "wasn't able", "was not able", "not able to", "didn't load",
            "did not load", "didn't return", "did not return", "timed out", "unreachable", "couldn't get", "could not get", "unable to get",
            "not accessible", "no content", "blank", "empty", "returned nothing", "unable to verify", "couldn't verify", "could not verify",
            "can't verify", "cannot verify", "couldn't reach", "could not reach", "unable to reach", "can't reach", "cannot reach",
            "wasn't accessible", "isn't loading", "not loading", "no text", "came back empty"]


def fail_words():
    return _caps(_FAIL_ZH + _FAIL_EN)


def is_zh(text):
    return len(re.findall(r"[一-鿿]", text)) >= 4


def fx(brand, url, title, snippet, content, date, error=None):
    """One web_fixture entry. url has no fragment; url_match is the scheme-less lowercase url."""
    e = {"query_match": brand, "url": url, "url_match": re.sub(r"^https?://", "", url).rstrip("/").lower(),
         "title": title, "snippet": snippet, "content": content.rstrip("\n") + "\n", "published_at": date}
    if error:
        e["error"] = error
    return e


def T(p, *, req=("web_fetch",), forb=("read_file", "search_text"), inc=(), any=(), exc=NOWEB, tok=None, review=None):
    return dict(p=p, req=list(req), forb=list(forb), inc=list(inc), any=list(any), exc=list(exc), tok=tok, review=review)


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
        if all(re.fullmatch(r"[\d,.]+", x) for x in t["any"]):
            e["output_contains_any_token"] = True
    if t["exc"]:
        e["output_excludes"] = t["exc"]
    return e


def allowed(n, rc, nfiles, multi):
    v = set()
    if n == 0 and rc <= 3:
        v.add("L0")
    if n == 1 and rc <= 4:
        v.add("L1")
    if n == 2 or (n == 1 and (nfiles >= 3 or rc >= 5)):
        v.add("L2")
    if n >= 3 or (multi and n >= 1) or rc >= 8:
        v.add("L3")
    return v


WF = {"must_offer": ["web_fetch", "read_file"]}
WFS = {"must_offer": ["web_fetch", "web_search", "read_file"]}


def mk(cid, *, sub, tt, desc, web, turns, traps, ref, why, trap_notes, policy=None, rc=2, files=None, compute=None, case_files=None,
       max_calls=None, derived=()):
    files = files or {}
    policy = policy or WF
    multi = len(turns) > 1
    for t in turns:
        low = re.sub(r"\s+", " ", t["p"].lower())
        for tool in TOOLS:
            assert tool not in low, (cid, tool)
        for trap in traps:
            for w in TRAP_WORDS[trap]:
                assert w.lower() not in low, (cid, trap, w)
        assert not re.search(r"测试|判据|verify|benchmark", low), (cid, t["p"])
        for x in t["inc"]:
            assert len(x) > 1 or x.isdigit(), (cid, x)
    ok = sorted(x for x in allowed(len(traps), rc, len(files), multi) if x != "L0")
    level = ok[0] if ok else "L0"
    axes = list(dict.fromkeys(["VER"] + [TRAP_AXIS[t] for t in traps]))
    digest = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    src = ""
    if compute:
        src = re.sub(r"^def \w+\(", "def compute(", textwrap.dedent(inspect.getsource(compute)), count=1)
        ns = {}
        exec(src, ns)
        final, _ = ns["compute"](dict(files), json.loads(json.dumps(web)))
        efiles = {}
        for path in files:
            if path not in final:
                efiles[path] = {"unchanged": True}
        for path, text in final.items():
            efiles[path] = {"equals": text}
        efiles.update(case_files or {})
        case_files = efiles
    v = ("import hashlib, json\n"
         "case = json.load(open(\"case.json\"))\n"
         "_pin = hashlib.sha256(json.dumps(case[\"files\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
         "assert _pin == %r, \"fixture changed\"\n"
         "page = \" \".join(w[\"content\"] + \" \" + w[\"snippet\"] for w in case[\"web_fixture\"]) + \" \" + \" \".join(case[\"files\"].values())\n"
         "prompts = \" \".join(t[\"prompt\"] for t in case[\"turns\"])\n"
         "for turn in case[\"turns\"]:\n"
         "    for item in turn[\"expect\"].get(\"output_contains\", []):\n"
         "        assert item in page or item in prompts or item in %s, item\n"
         "for url in [w[\"url\"] for w in case[\"web_fixture\"]]:\n"
         "    assert url, url\n" % (digest, json.dumps(list(derived), ensure_ascii=False)))
    if compute:
        v += (src + "\nFINAL, _ = compute(dict(case[\"files\"]), case[\"web_fixture\"])\n"
              "for path, rule in case[\"expect\"][\"files\"].items():\n"
              "    if \"equals\" in rule:\n"
              "        assert FINAL[path] == rule[\"equals\"], path\n"
              "    elif rule.get(\"unchanged\"):\n"
              "        assert path in case[\"files\"] and path not in FINAL, path\n"
              "print(json.dumps({\"files\": {k: FINAL[k] for k in case[\"expect\"][\"files\"] if k in FINAL}}, ensure_ascii=False))\n")
    else:
        anys = []
        for t in turns:
            for w in t["any"]:
                if w not in anys:
                    anys.append(w)
        incs = [x for t in turns for x in t["inc"]]
        if anys:
            v += "print(json.dumps({\"expected_contains_any\": %s}, ensure_ascii=False))\n" % json.dumps(anys, ensure_ascii=False)
        else:
            v += "print(json.dumps({\"expected_string\": %s}, ensure_ascii=False))\n" % json.dumps(incs[0], ensure_ascii=False)
    tl = []
    for t in turns:
        d = {"prompt": t["p"], "expect": _expect(t)}
        if t["review"]:
            d["review_before"] = t["review"]
        tl.append(d)
    p0 = turns[0]["p"]
    alts = [p0, "想确认一下：" + p0, p0 + "（简单说就行）", "麻烦帮我看看：" + p0, "再问一件事：" + p0]
    notes = "## Traps\n" + "".join("- %s\n" % x for x in trap_notes)
    notes += "\n## Reference solution\n" + ref.strip("\n") + "\n\n## Why the answer is unique\n" + why.strip("\n") + "\n"
    notes += "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, a.replace("\n", " ")) for i, a in enumerate(alts))
    cexp = {}
    if case_files:
        cexp["files"] = case_files
    if max_calls:
        cexp["max_calls"] = max_calls
    BATCH.write_case(cid, desc=desc, task_type=tt, family="b22b-%s-%s" % (sub, cid.split("-")[1][-3:]), level=level,
                     ref_calls=rc, files=files, turns=tl, verify=v, notes=notes, traps=list(traps),
                     decoys={t: DECOY[t] for t in traps}, axes=axes, answer_style="natural", web=web,
                     tool_policy=policy, case_expect=cexp or None, extra_tags={"batch": "b22b", "subtype": sub})
    META[cid] = {"sub": sub, "zh": is_zh(" ".join(t["p"] for t in turns)), "turns": len(turns), "level": level,
                 "len": len(turns[0]["p"])}


_MON = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def dates(iso):
    """Accepted spellings of an ISO date."""
    y, m, d = (int(x) for x in iso.split("-"))
    mn = _MON[m - 1]
    return [iso, "%d/%d/%d" % (y, m, d), "%d年%d月%d日" % (y, m, d), "%d 年 %d 月 %d 日" % (y, m, d), "%d月%d日" % (m, d), "%d 月 %d 日" % (m, d),
            "%d月%d号" % (m, d), "%s %d" % (mn, d), "%d %s" % (d, mn), "%s %d" % (mn[:3], d), "%d %s" % (d, mn[:3])]
