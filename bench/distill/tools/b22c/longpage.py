"""Assembles long fixture pages (over 3000 World tokens) from handwritten sections plus generated filler."""
import random

import filler
from common import est_tokens

TARGET = 3300


def compose(seed, lang, product, modules, domain, topics, head, key, tail=(), target=TARGET):
    """head/key/tail: lists of (heading, body). A changelog section is padded so the page reaches `target`
    estimated tokens before the key sections; comments and related links follow them."""
    rng = random.Random(seed)
    zh = lang == "zh"
    h2 = lambda t: "## " + t

    def render(sections):
        return "\n\n".join(h2(h) + "\n\n" + b.strip("\n") for h, b in sections)

    top = "# %s\n\n" % head[0][0] + head[0][1].strip("\n") + "\n\n" + render(head[1:])
    closing = [("读者评论" if zh else "Reader comments", filler.comments(rng, lang, 9)),
               ("相关阅读" if zh else "Related reading", filler.related(rng, lang, topics, 6, domain)),
               ("版权与声明" if zh else "Copyright", ("© 2026 %s 版权所有。本文档仅供参考，内容可能随版本调整。\n页面最后更新：2026-09-30。" % product) if zh
                else "© 2026 %s. All rights reserved. This page is informational and may change between releases.\nLast updated 2026-09-30." % product)]
    n = 6
    while True:
        log = filler.changelog(random.Random(seed + 1), product, modules, lang, n)
        page = top + "\n\n" + h2("更新记录" if zh else "Changelog") + "\n\n" + log + "\n\n" + render(key) + "\n\n" + render(tail) + ("\n\n" if tail else "") + render(closing) + "\n"
        if est_tokens(page) >= target:
            return page
        n += 3
