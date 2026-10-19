"""F2 helper: two or three long pages from different sites -> comparison."""
from common import T, est, mk
from f1 import NOTE_FILE, first_screen_ok
from pages import page, trajectory


def P(lang, url, q, title, topics, intro, sections, tokens, date, facts, seed=None):
    """One page spec; facts are the substrings (from this page) the answer must carry."""
    return dict(lang=lang, url=url, q=q, title=title, topics=topics, intro=intro, sections=sections, tokens=tokens,
                date=date, facts=list(facts), seed=seed)


def make_pages(cid, pages):
    """Builds the web_fixture entries; filler-only sections are put in front when a page's facts would sit in its first screen."""
    web = []
    for i, p in enumerate(pages):
        secs = list(p["sections"])
        for attempt in range(3):
            pg = page(p["seed"] or "%s-%d" % (cid, i), p["lang"], p["url"], p["q"], p["title"], p["topics"], p["intro"], secs,
                      p["tokens"], p["date"])
            try:
                first_screen_ok(pg["content"], p["facts"], minimum=1)
                break
            except AssertionError:
                secs = [("背景" if p["lang"] == "zh" else "Background", [])] + secs
        web.append(pg)
    return web


def F2(cid, pages, prompt, names=(), any=(), exc=(), out=None, traps=("TR-TRUNC", "TR-MULTISRC"), tt=None, with_url=True, reads=3):
    web = make_pages(cid, pages)
    inc = list(names) + [f for p in pages for f in p["facts"]]
    total = sum(est(w["content"]) for w in web)
    assert total <= 12000, (cid, total)
    turns = [T(prompt, inc=[] if out else inc, any=any, exc=exc, req=["web_fetch"])]
    est_t = trajectory([est(w["content"]) for w in web], reads, final=250 if out else 700, steps=2 if out else 0)
    must = ["web_fetch", "read_file"] + (["write_file"] if out else []) + ([] if with_url else ["web_search"])
    steps = ("%s 一次 web_fetch 同时取 %d 个页面（各存入 .web/，各返回开头和 outline）\n" % ("" if with_url else "web_search ->", len(pages)) +
             "read_file 按各页 outline 跳到后面的章节共 %d 次（或 search_text 在 .web 里搜）\n" % reads +
             ("write_file 写入 %s\n" % out if out else "") + "作答，说明哪个页面更新或更权威。")
    mk(cid, sub="F2", tt=tt or ("tool_then_write" if out else "summarize_page"),
       desc="Compare %d long pages from different sites" % len(pages), turns=turns, steps=steps,
       why="Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.",
       est_tokens=est_t, files=dict(NOTE_FILE) if out else None, web=web, rules={out: inc} if out else None, must=must, traps=traps,
       ref_calls=4 + reads + (1 if out else 0))
