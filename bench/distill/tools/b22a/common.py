"""b22a (v2.2: local search empty -> go online) shared helpers: case writer, word lists, fixture builders."""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch  # noqa: E402

BATCH = Batch(salt="b22a", author="llm:claude-sonnet-b22a", version="v2.2", tool_catalog="agent-tool-v3.1")
META = {}
DECOY = {"TR-ABSENT": "invented value", "TR-WEBSTALE": "the web page's different value"}
AXIS = {"TR-ABSENT": "DEC", "TR-WEBSTALE": "VER"}

# words that show the reply says where the value came from (A1): kept broad on purpose
SRC = ["网页", "网站", "官网", "页面", "搜索", "网上", "网络", "在线", "来源", "根据", "查到", "查询", "web", "website", "page", "online",
       "source", "according", "site", "official", "search", "http", "docs", "documentation", "found", "查了", "公告", "文档", "资料", "官方", "页", "站", "网", "查", "来自", "据", "per ", "from "]
SRC = list(dict.fromkeys(SRC + [w.capitalize() for w in SRC]))
LOCAL_TOOLS = ["list_files", "search_text", "read_file"]
ALL_TOOLS = LOCAL_TOOLS + ["web_search", "web_fetch"]
MON = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def is_zh(text):
    return len(re.findall(r"[一-鿿]", text)) >= 4


def dates(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    mn = MON[m - 1]
    return [iso, "%d/%d/%d" % (y, m, d), "%d年%d月%d日" % (y, m, d), "%d 年 %d 月 %d 日" % (y, m, d), "%d月%d日" % (m, d), "%d 月 %d 日" % (m, d),
            "%d月%d号" % (m, d), "%s %d" % (mn, d), "%d %s" % (d, mn), "%s %d" % (mn[:3], d), "%d %s" % (d, mn[:3]), "%d.%d.%d" % (d, m, y),
            "%s %d, %d" % (mn, d, y), "%s %d, %d" % (mn[:3], d, y),
            "%02d/%02d/%d" % (d, m, y), "%02d/%02d/%d" % (m, d, y), "%d/%02d/%02d" % (y, m, d), "%d.%02d.%02d" % (y, m, d)]


def fx(q, url, title, snippet, content, date):
    """One web_fixture entry. q: substring a search query must contain."""
    return {"query_match": q, "url": url, "url_match": re.sub(r"^https?://", "", url).rstrip("/"), "title": title,
            "snippet": snippet, "content": content.rstrip("\n") + "\n", "published_at": date}


def T(prompt, *, req=(), inc=(), any=(), exc=(), forb=()):
    return dict(prompt=prompt, req=list(req), inc=list(inc), any=list(any), exc=list(exc), forb=list(forb))


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


def _levels(n_traps, ref, n_files, multi):
    ok = set()
    if n_traps == 0 and ref <= 3:
        ok.add("L0")
    if n_traps == 1 and ref <= 4:
        ok.add("L1")
    if n_traps == 2 or (n_traps == 1 and (n_files >= 3 or ref >= 5)):
        ok.add("L2")
    if n_traps >= 3 or (multi and n_traps >= 1) or ref >= 8:
        ok.add("L3")
    return sorted(ok)


def mk(cid, *, sub, tt, desc, web, turns, files, policy, trap, ref, why, notes_extra, ref_calls, max_calls=None, n=0):
    """sub: A1/A2/A0. n: running number within the subtype (family name b22a-<sub>-<n>)."""
    multi = len(turns) > 1
    lv = [x for x in _levels(1, ref_calls, len(files), multi)]
    level = lv[0]
    page = " ".join(w["content"] + " " + w["snippet"] for w in web)
    flat = page + " " + " ".join(files.values()) + " " + " ".join(t["prompt"] for t in turns)
    for t in turns:
        for x in t["inc"]:
            assert len(x) > 1 or x.isdigit(), (cid, x)
            assert x in flat, (cid, x)
        for x in t["exc"]:
            assert x not in " ".join(t["inc"]), (cid, x)
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
         "text = \" \".join(w[\"content\"] + \" \" + w[\"snippet\"] for w in case[\"web_fixture\"]) + \" \" + \" \".join(case[\"files\"].values())\n"
         "for turn in case[\"turns\"]:\n"
         "    for item in turn[\"expect\"].get(\"output_contains\", []):\n"
         "        assert item in text or item in turn[\"prompt\"], item\n" % d)
    if srcs:
        v += "print(json.dumps({\"expected_string\": %s}, ensure_ascii=False))\n" % json.dumps(srcs[0], ensure_ascii=False)
    else:
        v += "print(json.dumps({\"expected_contains_any\": %s}, ensure_ascii=False))\n" % json.dumps(anyset, ensure_ascii=False)
    tl = [{"prompt": t["prompt"], "expect": _expect(t)} for t in turns]
    qm = web[0]["query_match"].lower() if web else ""
    p0 = next((t["prompt"] for t in turns if qm in t["prompt"].lower()), turns[0]["prompt"]).replace("\n", " ")
    alts = [p0, "想确认一下：" + p0, p0 + "（简单说就行）", "麻烦帮我看看：" + p0, "再问一件事：" + p0]
    notes = "## Traps\n- %s\n" % trap + "".join("- %s\n" % x for x in notes_extra)
    notes += "\n## Reference solution\n" + ref.strip("\n") + "\n\n## Why the answer is unique\n" + why.strip("\n") + "\n"
    notes += "\nExpected: " + " | ".join(srcs) + "\n"
    notes += "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, a) for i, a in enumerate(alts))
    expect = {"max_calls": max_calls} if max_calls else None
    BATCH.write_case(cid, desc=desc, task_type=tt, family="b22a-%s-%s" % (sub, cid.split("-")[1]), level=level, ref_calls=ref_calls,
                     files=files, turns=tl, verify=v, notes=notes, traps=[trap], decoys={trap: DECOY[trap]}, axes=[AXIS[trap]],
                     answer_style="natural", web=web, tool_policy=policy, case_expect=expect,
                     extra_tags={"batch": "b22a", "subtype": sub})
    META[cid] = {"sub": sub, "zh": is_zh(" ".join(t["prompt"] for t in turns)), "turns": len(turns), "level": level,
                 "chars": len(turns[0]["prompt"]), "scen": cid.split("-")[0]}
