#!/usr/bin/env python3
"""Generates doc-13313 (zh, travel policy: hotel cap, old 2025 table vs the July-2026 notice near the end)."""
import random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gen"))
from _lib import finish, check_size, offsets
from _doc import make_doc

CANARY = "EXAM-CANARY-6e0b92d7"
rng = random.Random(13313)
OLD = ["## 差旅住宿标准（2025版）", "", "生效日期：2025-03-01", "",
       "出差住宿费按城市档次设每晚报销上限，超出部分由个人承担：", "",
       "| 城市档次 | 每晚上限（元） |", "|---|---|",
       "| 一线城市（北京、上海、广州、深圳） | 650 |", "| 二线城市（省会及计划单列市） | 450 |", "| 其他城市 | 330 |", "",
       "出差餐补每天 100 元，市内交通凭票实报实销。"]
NEW = ["## 公告：2026年7月起差旅住宿标准调整", "", "生效日期：2026-07-01", "",
       "鉴于近一年酒店价格上涨，经管理层会议决定，自生效日期起出差住宿每晚上限调整如下，原《差旅住宿标准（2025版）》中的住宿上限条款同时废止：", "",
       "| 城市档次 | 每晚上限（元） |", "|---|---|",
       "| 一线城市（北京、上海、广州、深圳） | 780 |", "| 二线城市（省会及计划单列市） | 520 |", "| 其他城市 | 380 |", "",
       "餐补（每天 100 元）和市内交通报销规则不变。"]
text = make_doc(rng, "zh", "公司行政与差旅管理制度汇编", 88, {28: OLD, 78: NEW})
size = check_size(text, 30_000, 60_000)
o_old, o_new = offsets(text, "生效日期：2025-03-01")[0], offsets(text, "生效日期：2026-07-01")[0]
assert o_new >= 40_000 and o_old < o_new
assert text.count("每晚上限") >= 3
prompt = "下周我要去上海出差，住酒店一晚最多能报销多少钱？公司的差旅制度我放在 差旅管理制度.md 里了。"
expect = {"expected_number": 780, "tolerance": 0.001, "expected_number_in_text": True}
finish(HERE, "doc-13313", CANARY, "docs", "policy_lookup", ["TR-LONG", "TR-SUPERSEDE"],
       {"TR-LONG": 650, "TR-SUPERSEDE": 650}, "L2", {"差旅管理制度.md": text}, prompt, expect,
       "Find the hotel cap for tier-1 cities in a 50KB handbook where an old table and a later notice disagree.",
       '''doc = case["files"]["差旅管理制度.md"]
assert doc.startswith("# 公司行政与差旅管理制度汇编")
import re as _re
best = None
for sec in doc.split("\\n## "):
    m = _re.search(r"生效日期：(\\d{4}-\\d{2}-\\d{2})", sec)
    v = _re.search(r"一线城市[^|]*\\| (\\d+) \\|", sec)
    if m and v and (best is None or m.group(1) > best[0]):
        best = (m.group(1), int(v.group(1)))
print(json.dumps({"expected": best[1]}))''',
       '''## Traps
- TR-LONG: handbook is %d bytes (spec range 30-60KB, so the whole file fits in one 64KB read; the answer sits late: the old table at byte %d, the notice at byte %d). Models that skim the front or stop at the first hit land on the old table.
- TR-SUPERSEDE: the 2025 table says 650 for tier-1 cities; the notice effective 2026-07-01 (read from the text, not the file name) says 780 and explicitly retires the old clause. The prompt anchors the trip to "next week" (after 2026-07-01), so only 780 applies.
## Reference solution
1. search_text 一线城市 / 每晚上限 (hits both tables) 2. read the later section, take 780.
## Why the answer is unique
The newer notice explicitly abolishes the 2025 cap; Shanghai is listed under tier 1; the trip is after the effective date. 650 is only the retired value.''' % (size, o_old, o_new), axes=["LNG", "VER"])
print("ok", size, o_old, o_new)
