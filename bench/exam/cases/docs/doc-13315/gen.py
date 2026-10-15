#!/usr/bin/env python3
"""Generates doc-13315 (zh, after-sales policy: return window for opened electronics, old vs revised)."""
import random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gen"))
from _lib import finish, check_size, offsets
from _doc import make_doc

CANARY = "EXAM-CANARY-7a14e3c9"
rng = random.Random(13315)
OLD = ["## 无理由退货期限（2025年版）", "", "生效日期：2025-01-01", "",
       "自签收之日起计算，各类商品的无理由退货期限如下：", "",
       "| 商品状态 | 期限（天） |", "|---|---|",
       "| 未拆封的所有商品 | 7 |", "| 已拆封的电子类商品 | 3 |", "| 已拆封的服饰、家居类商品 | 5 |", "",
       "定制商品和生鲜食品不适用无理由退货。"]
NEW = ["## 修订通知：无理由退货期限调整", "", "生效日期：2026-08-01", "",
       "为提升客户体验，经售后委员会决议，自生效日期起以下期限调整，其余类别以及“定制商品和生鲜食品不适用”的约定不变；2025年版中对应条目同时作废：", "",
       "| 商品状态 | 期限（天） |", "|---|---|",
       "| 未拆封的所有商品 | 15 |", "| 已拆封的电子类商品 | 10 |", "",
       "已拆封的服饰、家居类商品仍为 5 天。"]
text = make_doc(rng, "zh", "客户服务与售后规定", 92, {30: OLD, 82: NEW})
size = check_size(text, 30_000, 60_000)
o_old, o_new = offsets(text, "生效日期：2025-01-01")[0], offsets(text, "生效日期：2026-08-01")[0]
assert o_new >= 40_000 and o_old < o_new
prompt = "有位客户上周三签收了一副蓝牙耳机，今天想无理由退货，包装已经拆了。按我们现在的售后规定，拆封的电子产品无理由退货最多几天？规定在 售后规定.md 里。"
expect = {"expected_number": 10, "tolerance": 0.001, "expected_number_in_text": True}
finish(HERE, "doc-13315", CANARY, "docs", "policy_lookup", ["TR-LONG", "TR-SUPERSEDE"],
       {"TR-LONG": 3, "TR-SUPERSEDE": 3}, "L2", {"售后规定.md": text}, prompt, expect,
       "Find the opened-electronics return window in a 50KB policy where the 2025 table was revised later.",
       '''import re as _re
doc = case["files"]["售后规定.md"]
assert doc.startswith("# 客户服务与售后规定")
best = None
for sec in doc.split("\\n## "):
    d = _re.search(r"生效日期：(\\d{4}-\\d{2}-\\d{2})", sec)
    v = _re.search(r"已拆封的电子类商品 \\| (\\d+) \\|", sec)
    if d and v and (best is None or d.group(1) > best[0]):
        best = (d.group(1), int(v.group(1)))
print(json.dumps({"expected": best[1]}))''',
       '''## Traps
- TR-LONG: file is %d bytes (spec range 30-60KB, so one 64KB read can hold it); the 2025 table is at byte %d, the revision at %d.
- TR-SUPERSEDE: the 2025 table says opened electronics 3 days; the revision effective 2026-08-01 says 10 and voids the old entry. The customer signed for the goods after the revision date (the clock is 2026-09-16, "last Wednesday" = 2026-09-09). Other numbers in the sections (7, 15, 5) are different categories.
## Reference solution
1. search_text 已拆封的电子类商品; 2. read both sections; use the one effective 2026-08-01: 10.
## Why the answer is unique
The revision explicitly replaces the 2025 entries; electronics opened = 10.''' % (size, o_old, o_new), axes=["LNG", "VER"])
print("ok", size, o_old, o_new)
