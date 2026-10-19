"""F1 helper: one or two long pages -> summary / report."""
from common import T, est, mk
from pages import page, trajectory

# second turn asked about the same page (answered from the archive with search_text/read_file or from what was read)
FOLLOW = {
    "web-34501": ("顺便问一下，团队版新增的冷存储层每 GB 每月多少钱？", ["0.03"]),
    "web-34502": ("The autosave interval changed too, right? What is it now?", ["30 seconds"]),
    "web-34504": ("手写笔套装要另外加多少钱？", ["299"]),
    "web-34505": ("And what yard utilisation did they report for the European terminals?", ["85"]),
    "web-34506": ("休学累计最多几个学期？复学要提前几个工作日申请？", ["4", "20"]),
    "web-34508": ("65 岁以上的老人坐这条线怎么收费？", ["免费"]),
    "web-34510": ("What discount do I get for paying by direct debit?", ["1.5"]),
    "web-34511": ("它支持多少种运动模式？", ["120"]),
    "web-34515": ("旺季的快船每天有几班？", ["7"]),
}
NOTE_FILE = {"team-wiki/drafts-index.txt": "Drafts in progress are listed here.\n"}


def tool_est(text):
    """The harness's own estimate (agent.EstimateTokens), which decides where web_fetch cuts the head."""
    return int(sum(0.25 if ord(c) < 128 else 1.1 for c in text))


def first_screen_ok(text, facts, minimum=2, edge=1250):
    pos = [tool_est(text[:text.index(f)]) for f in facts if f in text]
    late = sum(1 for p in pos if p > edge)
    assert late >= minimum, (facts, pos)


def F1(cid, lang, q, url, title, topics, intro, sections, prompt, inc, exc=(), out=None, tokens=5800, date="2026-09-20",
       with_url=True, tt=None, traps=("TR-TRUNC",), second=None, p2=None, inc2=(), seed=None, any=(), reads=2):
    """sections: [(heading, [fact paragraphs])]; inc must be substrings of fact paragraphs."""
    pg = page(seed or cid, lang, url, q, title, topics, intro, sections, tokens, date)
    web = [pg]
    first_screen_ok(pg["content"], list(inc))
    turns = [T(prompt, inc=[] if out else list(inc) + list(inc2), exc=exc, req=["web_fetch"], any=any)]
    if second:
        web.append(second)
        first_screen_ok(second["content"], list(inc2), minimum=0)
    if cid in FOLLOW:
        fp, finc = FOLLOW[cid]
        turns.append(T(fp, inc=finc))
    rules = {out: list(inc) + list(inc2)} if out else None
    pts = [est(w["content"]) for w in web]
    est_t = trajectory(pts, reads + (1 if second else 0), final=250 if out else 650, steps=2 if out else 0)
    if cid in FOLLOW:
        est_t += 2900
    must = ["web_fetch", "read_file"] + (["write_file"] if out else []) + ([] if with_url else ["web_search"])
    steps = ("%s web_fetch（长页面存入 .web/，只返回开头和 outline）\n" % ("web_search ->" if not with_url else "") +
             "read_file 按 outline 跳到后面的章节 %d 次（或 search_text 在 .web 里搜关键词）\n" % reads +
             ("write_file 写入 %s\n" % out if out else "") + "作答。" + ("\n第二轮追问同一页面的细节：search_text 在 .web 里搜或 read_file 跳读，再作答。" if cid in FOLLOW else ""))
    mk(cid, sub="F1", tt=tt or ("tool_then_write" if out else "summarize_page"), desc="Long page %s: %s" % (q, "report file" if out else "summary"),
       turns=turns, steps=steps, why="Facts are spread over several sections; at least two sit after the first 1200 tokens of the page.",
       est_tokens=est_t, files=dict(NOTE_FILE) if out else None, web=web, rules=rules, must=must, traps=traps,
       ref_calls=3 + reads + (1 if out else 0))
