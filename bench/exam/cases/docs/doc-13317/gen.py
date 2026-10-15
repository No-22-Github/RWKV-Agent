#!/usr/bin/env python3
"""Generates doc-13317 (zh, employee handbook: annual leave by tenure, old table vs 2026 revision)."""
import random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gen"))
from _lib import finish, check_size, offsets
from _doc import make_doc

CANARY = "EXAM-CANARY-95c2a0e6"
rng = random.Random(13317)
OLD = ["## 带薪年假天数（2024年版）", "", "施行日期：2024-04-01", "",
       "员工带薪年假按司龄分档，每个自然年度一次性发放：", "",
       "| 司龄 | 年假（天） |", "|---|---|",
       "| 满1年不满5年 | 5 |", "| 满5年不满10年 | 8 |", "| 满10年及以上 | 12 |", "",
       "当年未休完的年假可顺延至次年第一季度。"]
NEW = ["## 修订：带薪年假天数调整", "", "施行日期：2026-01-01", "",
       "公司从 2026 年度起提高年假标准，此表取代 2024 年版的全部档位，年度发放方式与顺延规则不变：", "",
       "| 司龄 | 年假（天） |", "|---|---|",
       "| 满1年不满5年 | 6 |", "| 满5年不满10年 | 11 |", "| 满10年及以上 | 15 |", "",
       "司龄以入职日起算，按完整年数计。"]
text = make_doc(rng, "zh", "员工手册（综合版）", 90, {29: OLD, 80: NEW})
size = check_size(text, 30_000, 60_000)
o_old, o_new = offsets(text, "施行日期：2024-04-01")[0], offsets(text, "施行日期：2026-01-01")[0]
assert o_new >= 40_000 and o_old < o_new
prompt = "我 2020 年 3 月入职的，到现在六年出头了。按公司现在的规定，我一年有几天带薪年假？手册我放在 员工手册.md 里了。"
expect = {"expected_number": 11, "tolerance": 0.001, "expected_number_in_text": True}
finish(HERE, "doc-13317", CANARY, "docs", "policy_lookup", ["TR-LONG", "TR-SUPERSEDE"],
       {"TR-LONG": 8, "TR-SUPERSEDE": 8}, "L2", {"员工手册.md": text}, prompt, expect,
       "Find the annual leave days for 5-10 years of tenure in a 50KB handbook with a 2024 table and a 2026 revision.",
       '''import re as _re
doc = case["files"]["员工手册.md"]
assert doc.startswith("# 员工手册（综合版）")
best = None
for sec in doc.split("\\n## "):
    d = _re.search(r"施行日期：(\\d{4}-\\d{2}-\\d{2})", sec)
    v = _re.search(r"满5年不满10年 \\| (\\d+) \\|", sec)
    if d and v and (best is None or d.group(1) > best[0]):
        best = (d.group(1), int(v.group(1)))
print(json.dumps({"expected": best[1]}))''',
       '''## Traps
- TR-LONG: handbook is %d bytes (within the 30-60KB range, so one 64KB read holds it); 2024 table at byte %d, 2026 revision at %d.
- TR-SUPERSEDE: the 2024 table gives 8 days for tenure 5-10 years; the revision effective 2026-01-01 gives 11 and replaces every tier. Tenure: joined 2020-03, now 2026-09 = 6 full years, so the 5-10 band applies (not 1-5, not 10+).
## Reference solution
1. search_text 满5年不满10年; 2. read both sections; the 2026-01-01 table says 11.
## Why the answer is unique
Tenure is a full 5 years (the prompt says a bit over six years), band 5-10; the 2026 table replaces the 2024 one.
## Teacher result
r1 (prompt said joined 2020-11): DeepSeek answered 8 from the 2024 table but passed by accident because "11" appeared in the prompt date (expected_number_in_text). Prompt changed to 2020-03; r2 passes with 11 and cites the 2026 revision.''' % (size, o_old, o_new), axes=["LNG", "VER"])
print("ok", size, o_old, o_new)
