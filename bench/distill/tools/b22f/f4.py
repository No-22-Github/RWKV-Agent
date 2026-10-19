"""F4 helper: long multi-turn sessions whose last turn needs a fact from the first turn."""
from common import T, est, mk
from f1 import first_screen_ok
from pages import BASE, HEAD, page


def money(n):
    return [str(n), "{:,}".format(n)]


def F4(cid, lang, files, web, turns, rules=None, tt="multi_turn", must=("read_file", "web_fetch"), edits=0, calcs=0, steps_text="", why="",
       max_calls=None, never=(), derived=()):
    """web: fx dicts (already built); turns: T() list. Estimated tokens: system + each long page's fetch and one
    max-size read, the small files, a few hundred tokens per step and per final answer."""
    for w in web:
        first_screen_ok(w["content"], [], minimum=0)
    total = BASE + sum(est(t["p"]) + 60 for t in turns)
    for w in web:
        pt = est(w["content"])
        total += (HEAD + min(pt - 1200, 3600)) if pt > 3000 else pt
    total += sum(min(est(c), 1500) for c in files.values()) + 260 * len(turns)
    total += 320 * (len(turns) + len(web) + edits + calcs + 1) + 450 * edits
    mk(cid, sub="F4", tt=tt, desc="Long %d-turn session; the last turn needs a fact from the first" % len(turns), turns=turns, steps=steps_text,
       why=why, est_tokens=int(total), files=files, web=web, rules=rules, must=list(must), never=list(never),
       traps=("TR-TRUNC", "TR-MULTISRC"), ref_calls=len(turns) + len(web) + edits + calcs + 2, max_calls=max_calls, derived=derived)


def price_case(cid, lang, *, csv_path, header, rows, key, qty, price, unit_word, site, url, title, topics, page_intro, sections_before, sections_after,
               decoys, p1, p2, p3, p4, over_words, under_words, date="2026-10-12", tokens=4800, qword="", seed=None):
    """rows: list of (item, budget) incl. key; page has the real price in a late section and decoy SKU prices elsewhere."""
    zh = lang == "zh"
    budget = dict(rows)[key]
    total = qty * price
    diff = abs(budget - total)
    files = {csv_path: header + "\n" + "\n".join("%s,%d" % (a, b) for a, b in rows) + "\n"}
    fact = ("%s的报价为每%s %d 元。" if zh else "%s is priced at %d dollars per %s.")
    sec = [(h, [f]) for h, f in sections_before]
    sec.append((sections_after[0][0], [(fact % (key, unit_word, price)) if zh else (fact % (key, price, unit_word))]))
    sec += [(h, [f]) for h, f in sections_after[1:]]
    sec += [(h, [f]) for h, f in decoys]
    pg = page(seed or cid, lang, url, site, title, topics, page_intro, sec, tokens, date)
    first_screen_ok(pg["content"], [str(price)], minimum=1)
    turns = [T(p1, inc=[str(budget)] if budget < 1000 else [], any=money(budget) if budget >= 1000 else [], anytok=budget >= 1000, req=["read_file"]),
             T(p2, inc=[str(price)] if price < 1000 else [], any=money(price) if price >= 1000 else [], anytok=price >= 1000, req=["web_fetch"]),
             T(p3, any=money(total), anytok=True),
             T(p4, any=money(diff), anytok=True)]
    return F4(cid, lang, files, [pg], turns, why="The last turn compares the web price total with the budget read in the first turn.",
              steps_text="turn1 read_file 读预算表；turn2 web_fetch 长页面 -> read_file 跳到价格章节；turn3 算总价；turn4 与第一轮预算比较，差额 %d" % diff,
              must=("read_file", "web_fetch", "calculator"), calcs=1)
