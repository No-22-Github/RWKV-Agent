"""b21i (v2.1 wave 3: web pages) shared helpers: case writer, word lists, fixture builders."""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch  # noqa: E402

BATCH = Batch(salt="b21i", author="llm:claude-sonnet-b21i", version="v2.1", tool_catalog="work-v2")
EXTRA = {"batch": "b21i"}
META = {}
DECOY = {"TR-WEBSTALE": "stale or unreleased value", "TR-MULTISRC": "the other source's value", "TR-FETCHFAIL": "invented page content",
         "TR-ABSENT": "invented value", "TR-DECOY": "neighbouring item value", "TR-SNIPPETVAGUE": "guess from snippet", "TR-EARLYHIT": "second-guessing a snippet answer"}


def _caps(ws):
    out = []
    for w in ws:
        out += [w, w.capitalize()]
        if "'" in w:
            out += [w.replace("'", "’"), w.capitalize().replace("'", "’")]
    return list(dict.fromkeys(out))


_FAIL_ZH = ["打不开", "无法打开", "没能打开", "未能打开", "没法打开", "无法访问", "没法访问", "访问失败", "访问不了", "抓取失败", "获取失败",
            "读取失败", "加载失败", "打开失败", "拉取失败", "无法获取", "没能获取", "未能获取", "没有获取", "没获取到", "获取不到", "取不到",
            "无法读取", "没能读取", "未能读取", "无法加载", "没能加载", "未能成功", "没有成功", "未成功", "没成功", "502", "报错", "出错", "错误",
            "失败", "不可用", "暂时无法", "暂时打不开", "没拿到", "没有拿到", "没能看到", "无法查看", "没法查看", "没读到", "没有读到", "读不到",
            "无法确认", "没法确认", "无法核实", "没法核实", "无法验证", "没有核实", "未核实", "未能核实", "没能核实", "没能确认", "未能确认"]
_FAIL_EN = ["couldn't open", "could not open", "can't open", "cannot open", "unable to open", "unable to load", "couldn't load",
            "could not load", "can't load", "cannot load", "couldn't fetch", "could not fetch", "unable to fetch", "failed",
            "failure", "error", "502", "bad gateway", "couldn't access", "could not access", "unable to access", "can't access",
            "cannot access", "unable to retrieve", "couldn't retrieve", "could not retrieve", "unable to read", "couldn't read",
            "could not read", "unavailable", "not available", "wasn't able", "was not able", "weren't able", "not able to",
            "didn't load", "did not load", "didn't return", "timed out", "unreachable", "couldn't get", "could not get",
            "unable to get", "wasn't accessible", "isn't loading", "not loading", "unable to verify", "couldn't verify",
            "could not verify", "can't verify", "cannot verify", "unable to confirm", "couldn't confirm", "could not confirm",
            "can't confirm", "cannot confirm", "unable to view", "couldn't view", "didn't succeed", "did not succeed",
            "was unsuccessful", "not accessible", "not reachable", "unable to pull", "couldn't pull"]
_ABS_ZH = ["没有搜到", "没搜到", "搜不到", "搜索不到", "没有搜索到", "没有找到", "没找到", "找不到", "未找到", "没有相关", "没有结果", "无结果",
           "没有任何结果", "没有查到", "没查到", "查不到", "没有检索到", "没检索到", "检索不到", "没有符合", "没有匹配", "没有收录",
           "未收录", "没有发现", "没发现", "未发现", "结果为空", "空结果", "返回为空", "没有返回", "没有可用", "没有对应", "无相关",
           "没有搜索结果", "搜索结果为空", "没有出现", "未出现", "找不着", "没有看到", "没看到", "未能找到", "没能找到", "无法找到",
           "没有任何", "什么都没", "无法查到", "无法搜索到", "没有该", "没有这个", "查无"]
_ABS_EN = ["no results", "no result", "nothing came back", "came back empty", "returned nothing", "returned no", "came up empty",
           "didn't find", "did not find", "couldn't find", "could not find", "can't find", "cannot find", "unable to find",
           "not find", "no matching", "no relevant", "no pages", "no page", "found nothing", "nothing found", "nothing relevant",
           "no hits", "no such", "not found", "empty", "didn't return", "did not return", "wasn't able to find", "was not able to find",
           "no information", "no source", "no sources", "no search", "doesn't appear", "does not appear", "isn't indexed",
           "not indexed", "no listing", "no record", "no data", "nothing on", "couldn't locate", "could not locate", "unable to locate",
           "no mention", "didn't turn up", "did not turn up", "didn't surface", "no official page", "no public"]


def fail_words():
    return _caps(_FAIL_ZH + _FAIL_EN)


def absent_words():
    return _caps(_ABS_ZH + _ABS_EN)


def is_zh(text):
    return len(re.findall(r"[一-鿿]", text)) >= 4


def fx(q, url, title, snippet, content, date, error=None):
    """One web_fixture entry. q: substring a search query must contain; url: advertised address."""
    e = {"query_match": q, "url": url, "url_match": re.sub(r"^https?://", "", url).rstrip("/"),
         "title": title, "snippet": snippet, "content": content.rstrip("\n") + "\n", "published_at": date}
    if error:
        e["error"] = error
    return e


def T(prompt, *, req=(), inc=(), any=(), exc=(), first=(), forb=(), tok=None, review=None):
    """One turn. req=required_tools, inc=output_contains (all), any=output_contains_any, exc=output_excludes,
    first=output_first_line_contains_any, forb=forbidden_tools."""
    return dict(prompt=prompt, req=list(req), inc=list(inc), any=list(any), exc=list(exc), first=list(first),
                forb=list(forb), tok=tok)


def _expect(t):
    e = {}
    if t["req"]:
        e["required_tools"] = t["req"]
    if t["forb"]:
        e["forbidden_tools"] = t["forb"]
    if t["inc"]:
        e["output_contains"] = t["inc"]
        # a number or ASCII identifier must match as a whole token; a Han neighbour counts as a boundary
        tok = t["tok"]
        if tok is None:
            tok = all(x.isascii() for x in t["inc"]) or any(re.fullmatch(r"[\d.]+", x) for x in t["inc"])
        if tok:
            e["output_contains_token"] = True
    if t["any"]:
        e["output_contains_any"] = t["any"]
    if t["exc"]:
        e["output_excludes"] = t["exc"]
    if t["first"]:
        e["output_first_line_contains_any"] = t["first"]
    return e


def mk(cid, *, tt, desc, web, turns, traps, ref, why, trap_notes, policy, level, ref_calls, files=None, axes=("VER",), sub=""):
    files = files or {}
    AX = {"TR-WEBSTALE": "VER", "TR-MULTISRC": "CHN", "TR-FETCHFAIL": "ERR", "TR-ABSENT": "DEC", "TR-DECOY": "OBS",
          "TR-SNIPPETVAGUE": "VER", "TR-EARLYHIT": "STP"}
    axes = list(dict.fromkeys(list(axes) + [AX[t] for t in traps]))
    multi = len(turns) > 1
    n = len(traps)
    ok = set()
    if n == 0 and ref_calls <= 3:
        ok.add("L0")
    if n == 1 and ref_calls <= 4:
        ok.add("L1")
    if n == 2 or (n == 1 and (len(files) >= 3 or ref_calls >= 5)):
        ok.add("L2")
    if n >= 3 or (multi and n >= 1) or ref_calls >= 8:
        ok.add("L3")
    level = sorted(x for x in ok if x != "L0")[0]
    for t in turns:
        for x in t["inc"]:
            assert len(x) > 1 or x.isdigit(), (cid, x)
    page = " ".join(w["content"] + " " + w["snippet"] for w in web)
    srcs = [x for t in turns for x in t["inc"]]
    anyset = []
    for t in turns:
        for w in t["any"]:
            if w not in anyset:
                anyset.append(w)
    d = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    v = ("import hashlib, json\n"
         "case = json.load(open(\"case.json\"))\n"
         "_pin = hashlib.sha256(json.dumps(case[\"files\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
         "assert _pin == %r, \"fixture changed\"\n"
         "page = \" \".join(w[\"content\"] + \" \" + w[\"snippet\"] for w in case[\"web_fixture\"])\n"
         "for turn in case[\"turns\"]:\n"
         "    for item in turn[\"expect\"].get(\"output_contains\", []):\n"
         "        assert item in page or item in %s, item\n" % (d, json.dumps([p for t in turns for p in [t["prompt"]]], ensure_ascii=False)))
    if anyset and not srcs:
        v += "print(json.dumps({\"expected_contains_any\": %s}, ensure_ascii=False))\n" % json.dumps(anyset, ensure_ascii=False)
    elif srcs:
        v += "print(json.dumps({\"expected_string\": %s}, ensure_ascii=False))\n" % json.dumps(srcs[0], ensure_ascii=False)
    else:
        raise ValueError(cid)
    tl = [{"prompt": t["prompt"], "expect": _expect(t)} for t in turns]
    p0 = turns[0]["prompt"].replace("\n", " ")
    alts = [p0, "想确认一下：" + p0, p0 + "（简单说就行）", "麻烦帮我看看：" + p0, "再问一件事：" + p0]
    notes = "## Traps\n" + "".join("- %s\n" % x for x in trap_notes)
    notes += "\n## Reference solution\n" + ref.strip("\n") + "\n\n## Why the answer is unique\n" + why.strip("\n") + "\n"
    notes += "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, a) for i, a in enumerate(alts))
    BATCH.write_case(cid, desc=desc, task_type=tt, family="b21i-%s-%s" % (sub or tt, cid.split("-")[1]), level=level,
                     ref_calls=ref_calls, files=files, turns=tl, verify=v, notes=notes, traps=list(traps),
                     decoys={t: DECOY[t] for t in traps}, axes=list(axes), answer_style="natural", web=web,
                     tool_policy=policy, extra_tags=EXTRA)
    META[cid] = {"tt": tt, "sub": sub, "zh": is_zh(" ".join(t["prompt"] for t in turns)), "turns": len(turns), "level": level,
                 "pol": "+".join(policy.get("must_offer", []))}


WS = {"must_offer": ["web_search"]}
WSF = {"must_offer": ["web_search", "web_fetch"]}


_MON = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def dates(iso):
    """Accepted spellings of an ISO date, for output_contains_any."""
    y, m, d = (int(x) for x in iso.split("-"))
    mn = _MON[m - 1]
    return [iso, "%d/%d/%d" % (y, m, d), "%d年%d月%d日" % (y, m, d), "%d 年 %d 月 %d 日" % (y, m, d), "%d月%d日" % (m, d), "%d 月 %d 日" % (m, d),
            "%d月%d号" % (m, d), "%s %d" % (mn, d), "%d %s" % (d, mn), "%s %d" % (mn[:3], d), "%d %s" % (d, mn[:3]), "%d.%d.%d" % (d, m, y)]
