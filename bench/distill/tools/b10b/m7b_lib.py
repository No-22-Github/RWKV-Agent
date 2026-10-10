"""Shared builders for b10b m7b: unverified-secondary-source and preview-vs-stable cases."""
import json

from common import revised
REV = {}
write_case = revised(REV)

UNVER_ZH = ["未核实", "没有核实", "无法核实", "没能核实", "未能核实", "没法核实", "未经官方", "没有经过官方", "未得到官方", "尚未经官方",
            "无法确认", "没能确认", "未能确认", "没法确认", "未经证实", "无法证实", "不能确认", "未在官方"]
UNVER_EN = ["unverified", "not verified", "couldn't verify", "could not verify", "unable to verify", "not been verified", "can't verify",
            "cannot verify", "couldn't confirm", "could not confirm", "can't confirm", "cannot confirm", "unable to confirm",
            "not confirmed", "unconfirmed", "not been confirmed"]
UNVER_EN = UNVER_EN + [w.replace("'", "\u2019") for w in UNVER_EN if "'" in w]  # curly apostrophe


def phr(items):
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, x) for i, x in enumerate(items))


def entry(q, host, title, snip, date, content=None, error=None):
    d = {"query_match": q, "url_match": host, "url": "https://" + host, "title": title, "snippet": snip, "published_at": date}
    if error:
        d["error"] = error
    else:
        d["content"] = content
    return d


def selfcheck(cid, expect, answer):
    for s in expect.get("output_contains", []):
        assert s in answer, (cid, "missing", s)
    any_ = expect.get("output_contains_any")
    if any_:
        assert any(s in answer for s in any_), (cid, "no any")
    for s in expect.get("output_excludes", []):
        assert s not in answer, (cid, "excluded", s)
    assert len(answer) <= expect["max_output_chars"]


def unver(cid, *, zh, slug, brand, prompt, off, err, sec, value, claim, answer, desc, phrs, files=None, hyb=False,
          ttype="lookup_value", ref_calls=3, level="L1", files_check=""):
    """off/sec: dict(host,title,snip,date[,body]). claim: sentence in the secondary page containing value."""
    web = [entry(brand, off["host"], off["title"], off["snip"], off["date"], error=err),
           entry(brand, sec["host"], sec["title"], sec["snip"], sec["date"], content=sec["body"])]
    expect = {"output_contains": [value], "output_contains_any": UNVER_ZH if zh else UNVER_EN,
              "required_tools": ["web_fetch"], "max_output_chars": 600}
    selfcheck(cid, expect, answer)
    verify = '''
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if %r in w["url"]][0]
sec = [w for w in case["web_fixture"] if %r in w["url"]][0]
assert off.get("error") and not off.get("content")
assert %r in sec["content"]
%s
print(json.dumps({"expected_string": %r}, ensure_ascii=False))
''' % (off["host"], sec["host"], claim, files_check, value)
    notes = '''
## Traps
- TR-FETCHFAIL: the official page https://%s fails to load (%s). The only readable source is the secondary page https://%s, which states %s.

## Reference solution
1. Search the topic: the official page and a secondary page are listed.
2. Fetch the official page: fails (%s).
3. Fetch the secondary page: it gives %s.%s
Final answer: %s
Criteria: contains %s plus an unverified/cannot-confirm phrase; a fetch happened.

## Why the answer is unique
The official source is unreachable, so the only obtainable value is the secondary page's; it has to be given with the caveat that it was not checked against the official page, not stated as fact and not replaced by "unknown".
''' % (off["host"], err, sec["host"], value, err, value, "\n4. Read the local file to identify the exact item." if hyb else "", answer, value) + phr(phrs)
    write_case(cid, desc=desc, task_type=ttype, family="fam-%s-b10b-%s-01" % (cid.split("-")[0], slug), level=level,
               ref_calls=ref_calls, traps=["TR-FETCHFAIL"], decoys={"TR-FETCHFAIL": "UNKNOWN"}, axes=["ERR"], web=web,
               files=files or {}, turns=[{"prompt": prompt, "expect": expect}], verify=verify, notes=notes)


def _stable_page(style, zh, name, stable, sdate, prev, ptag, pdate, old):
    if style == 0:
        h = "| 版本 | 通道 | 日期 |" if zh else "| Version | Channel | Date |"
        pc = ptag + ("（不建议用于生产）" if zh else " (not for production)")
        return "# %s %s\n\n%s\n|---|---|---|\n| %s | %s | %s |\n| %s | stable | %s |\n| %s | stable | 2026-06-18 |\n" % (
            name, "发布记录" if zh else "releases", h, prev, pc, pdate, stable, sdate, old)
    if style == 1:
        return "# %s changelog\n\n## %s (%s) %s\n%s\n\n## %s (latest) %s\n%s\n\n## %s %s\n%s\n" % (
            name, prev, ptag, pdate, "预览阶段，接口可能变动，不建议用于生产。" if zh else "Early access. APIs may change; not recommended for production.",
            stable, sdate, "当前稳定版本，推荐生产使用。" if zh else "Current stable release, recommended for production.", old, "2026-06-18", "修复若干问题。" if zh else "Bug fixes.")
    if style == 2:
        if zh:
            return "# 下载 %s\n\n生产环境推荐：%s（stable，%s 发布）\n\n抢先体验：%s（%s，%s 发布），仅供评估，不提供支持。\n\n历史版本：%s\n" % (
                name, stable, sdate, prev, ptag, pdate, old)
        return "# Download %s\n\nRecommended for production: %s (stable, released %s)\n\nEarly access: %s (%s, released %s) - evaluation only, unsupported.\n\nPrevious: %s\n" % (
            name, stable, sdate, prev, ptag, pdate, old)
    if zh:
        return "# %s 版本通道\n\n- %s — %s，%s，尚未定稿\n- %s — stable，%s，客户可正式使用\n- %s — stable，2026-06-18，上一个稳定版本\n" % (
            name, prev, ptag, pdate, stable, sdate, old)
    return "# %s release channels\n\n- %s - %s, %s, not final\n- %s - stable, %s, safe for customers\n- %s - stable, 2026-06-18, previous stable\n" % (
        name, prev, ptag, pdate, stable, sdate, old)


def preview(cid, *, zh, slug, style, brand, host, name, stable, sdate, prev, ptag, pdate, old, prompt, blog=None, phrs,
            desc, files=None, deployed=None, files_check="", ref_calls=2, ttype="latest_version", level="L1"):
    """blog: (host, title, text) of a secondary page promoting the preview."""
    web = [entry(brand, host, name + (" 发布记录" if zh else " releases"), name + (" 各通道版本。" if zh else " versions by channel."),
                 pdate, content=_stable_page(style, zh, name, stable, sdate, prev, ptag, pdate, old))]
    if blog:
        web.append(entry(brand, blog[0], blog[1], blog[2][:60], pdate, content="# %s\n\n%s\n" % (blog[1], blog[2])))
    contains = [stable] + ([deployed] if deployed else [])
    if zh:
        ex = [prev + s for s in (" 是最新的正式", " 是正式版", " 是最新正式", " 就是正式", " 为正式版")]
    else:
        ex = [prev + s for s in (" is the latest stable", " is stable", " is the current stable", " is the stable release")]
    expect = {"output_contains": contains, "output_excludes": ex, "required_tools": ["web_fetch"], "max_output_chars": 600}
    if zh:
        answer = "%s%s现在客户能正式用的最新稳定版是 %s（%s 发布）；%s 只是 %s 通道的预览版，不建议给生产环境。" % (
            "清单里" + name + "现在装的是 " + deployed + "，" if deployed else "", name, stable, sdate, prev, ptag)
    else:
        answer = "%sThe newest stable %s release customers can use is %s (released %s); %s is only on the %s channel and is not for production." % (
            ("Your manifest has %s on %s. " % (name, deployed)) if deployed else "", name, stable, sdate, prev, ptag)
    selfcheck(cid, expect, answer)
    verify = '''
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if %r in w["url"]][0]["content"]
assert %r in off and %r in off and %r in off
line = [l for l in off.splitlines() if %r in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))
%s
print(json.dumps({"expected_string": %r}, ensure_ascii=False))
''' % (host, stable, prev, old, stable, files_check, stable)
    notes = '''
## Traps
- TR-SUPERSEDE: the official page lists %s (%s) above the stable line; customers can only use the latest stable, %s.%s

## Reference solution
1. Search %s versions: the official release page%s.
2. Fetch https://%s: stable %s (%s), preview %s.%s
Final answer: %s
Criteria: contains %s%s; does not call %s the stable version; a fetch happened.

## Why the answer is unique
The question restricts to what customers/production can use, i.e. the stable channel; the only newer entry is a %s build, so %s is the single correct version.
''' % (prev, ptag, stable, " A blog post promotes the preview." if blog else "", name, " and a blog post" if blog else "", host, stable, sdate,
       prev, "\n3. Read the local manifest for the installed version %s." % deployed if deployed else "", answer, stable,
       (" and %s" % deployed) if deployed else "", prev, ptag, stable) + phr(phrs)
    write_case(cid, desc=desc, task_type=ttype, family="fam-%s-b10b-%s-01" % (cid.split("-")[0], slug), level=level,
               ref_calls=ref_calls, traps=["TR-SUPERSEDE"], decoys={"TR-SUPERSEDE": prev}, axes=["VER"], web=web,
               files=files or {}, turns=[{"prompt": prompt, "expect": expect}], verify=verify, notes=notes)
