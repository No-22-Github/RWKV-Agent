"""Case-shape helpers for the three subtypes (A1 local empty -> web, A2 prompt says nothing local -> web at once, A0 control)."""
import re
from common import *

_N = {"A1": 0, "A2": 0, "A0": 0}


def _page(brand, pages):
    q = brand.split()[0] if (" " in brand and brand.isascii()) else brand
    return [fx(q, u, t, s, c, d) for (u, t, d, s, c) in pages]


_UNIT = re.compile(r"^(\d+(?:\.\d+)?) ?(元|天|公斤|折|GB|MB|dollars|pounds)$")


def _bare(v):
    m = _UNIT.match(v)
    return m.group(1) if m else v


def _ans(val, date_any):
    """val: str answer (inc) ; date_any: list of date spellings (any)."""
    return dict(inc=[_bare(val)] if val else [], any=date_any or [])


def a1(cid, tt, brand, p1, files, pages, val=None, dany=None, p2=None, val2=None, dany2=None, req2=("web_search",), rev=None, fetch=False):
    """A1: workspace has related files without the answer; the answer lives only on the web.
    rev=(prompt, value, files-note): reversed order - turn 1 is a local question (answer in files), turn 2 external."""
    _N["A1"] += 1
    web = _page(brand, pages)
    ans1 = _ans(val, dany)
    req = ["web_search"] + (["web_fetch"] if fetch else [])
    t1 = T(p1, req=req, inc=ans1["inc"], any=ans1["any"] or SRC)
    turns = [t1]
    mc = {"search_text": 2, "list_files": 2}
    if rev:
        lp, lval = rev
        turns = [T(lp, inc=[lval], forb=["web_search", "web_fetch"]), t1]
        mc = {"search_text": 3, "list_files": 3}
    if p2:
        a2 = _ans(val2, dany2)
        turns.append(T(p2, req=list(req2), inc=a2["inc"], any=a2["any"]))
    ref = "list_files/search_text 至多各 2 次确认本地没有答案 -> web_search" + (" -> web_fetch" if fetch else "") + " -> 作答并说明本地没有、答案来自网页" + ("；追问再查网页" if p2 else "")
    mk(cid, sub="A1", tt=tt, desc="Related local files lack the answer; the model checks locally once or twice then goes online (%s)" % brand,
       web=web, turns=turns, files=files, policy={"must_offer": ALL_TOOLS}, trap="TR-ABSENT", ref=ref,
       why="The value exists only in the web fixture; the workspace files mention the topic but never state it.",
       notes_extra=["工作区文件相关但不含答案；走捷径说『工作区里没有』或在本地反复换词搜索都过不了判据。"],
       ref_calls=5 if p2 else (4 if fetch else 3), max_calls=mc, n=_N["A1"])


def a2(cid, tt, brand, p1, files, pages, val=None, dany=None, p2=None, val2=None, dany2=None, fetch=False, req2=("web_search",)):
    """A2: the prompt already says nothing local / asks to look it up online -> first call must be web_search."""
    _N["A2"] += 1
    web = _page(brand, pages)
    a = _ans(val, dany)
    req = ["web_search"] + (["web_fetch"] if fetch else [])
    turns = [T(p1, req=req, inc=a["inc"], any=a["any"], forb=LOCAL_TOOLS)]
    if p2:
        b = _ans(val2, dany2)
        turns.append(T(p2, req=list(req2), inc=b["inc"], any=b["any"], forb=LOCAL_TOOLS))
    mk(cid, sub="A2", tt=tt, desc="The user says there is nothing local; the first and only data source is the web (%s)" % brand,
       web=web, turns=turns, files=files, policy={"must_offer": ALL_TOOLS}, trap="TR-ABSENT",
       ref="第一步直接 web_search" + (" -> web_fetch" if fetch else "") + " -> 作答" + ("；追问再查网页" if p2 else ""),
       why="Prompt says the workspace has no such material; the value is in the web fixture only.",
       notes_extra=["题面已说明本地没有资料；碰本地工具（list_files/search_text/read_file）即判错。"],
       ref_calls=3 if p2 else (3 if fetch else 2), max_calls=None, n=_N["A2"])


def _exc(xs):
    out = []
    for x in xs:
        out.append(x)
        if " " in x and not x.isascii() or re.search(r"\d \S", x):
            out.append(x.replace(" ", ""))
    return list(dict.fromkeys(out))


def a0(cid, tt, brand, p1, files, pages, val, exc, p2=None, val2=None, dany2=None, req2=("web_search",), dany=None):
    """A0 control: the answer is in the workspace and the prompt points at it; the web page carries a different value."""
    _N["A0"] += 1
    web = _page(brand, pages)
    turns = [T(p1, inc=[_bare(val)] if val else [], any=dany or [], exc=_exc(exc), forb=["web_search", "web_fetch"])]
    if p2:
        b = _ans(val2, dany2)
        turns.append(T(p2, req=list(req2), inc=b["inc"], any=b["any"]))
    mk(cid, sub="A0", tt=tt, desc="Control: the answer is in the workspace file the user means; going online would yield a different value (%s)" % brand,
       web=web, turns=turns, files=files, policy={"must_offer": ALL_TOOLS}, trap="TR-WEBSTALE",
       ref="list_files/search_text 找到文件 -> read_file 读出 -> 直接作答（不上网）" + ("；第二轮追问外部信息再 web_search" if p2 else ""),
       why="The user's own file states the value; the web fixture deliberately carries a different one.",
       notes_extra=["对照组：题面指的是『我们项目里/这份文件里的』值；上网拿到的是另一个数。"],
       ref_calls=4 if p2 else 3, max_calls=None, n=_N["A0"])
