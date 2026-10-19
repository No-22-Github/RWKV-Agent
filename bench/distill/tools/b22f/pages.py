"""Page and path helpers shared by the b22f case modules."""
from common import est, fx
from gen import Gen

BASE = 1500       # system prompt + tool directory (row 0 of a replayed case: 1516 tokens)
STEP = 350        # one assistant step: reasoning + tool call
HEAD = 1400       # web_fetch result for a long page: opening 1200 + outline + note (measured 1381)


def page(seed, lang, url, q, title, topics, intro, sections, tokens, date, snippet=None, noise=True):
    g = Gen(seed, lang, topics)
    tokens = min(tokens, 5900)   # real RWKV tokens; the brief caps a page at 6000
    body = g.page(title, intro, sections, tokens, noise=noise)
    return fx(q, url, title, snippet or ("概述页面，具体内容见正文。" if lang == "zh" else "Overview page; details are in the body."), body, date)


def trajectory(pages_tokens, reads, user=150, final=550, extra=0, steps=None, cap=4000):
    """Estimated trajectory tokens of the reference path: each long page costs HEAD for the fetch
    plus `reads` read_file/search_text results of about 2400 tokens (capped by what is left of the page)."""
    total = BASE + user + STEP
    left = 0
    for pt in pages_tokens:
        total += HEAD if pt > 3000 else pt
        left += max(0, pt - 1200)
    total += min(left, reads * cap) + reads * STEP + final + (steps or 0) * STEP + extra
    return int(total)
