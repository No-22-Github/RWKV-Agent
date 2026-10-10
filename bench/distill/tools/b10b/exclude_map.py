#!/usr/bin/env python3
"""S5 reading verdicts for b10b (see tools/exclude_lib.py). Run from the repo root."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exclude_lib import run  # noqa: E402

MANUAL = {
    ("hyb-8025", "orig", 1): "把官网标注 10 月 1 日起执行的新价当成现行价（今天 9 月 16 日），同题 p2 正确指出尚未生效",
    ("web-8074", "orig", 1): "中文题第一次搜索用日文（嵐山マラソン…）",
    ("web-8041", "fix", 1): "终答把官网域名拼错成 haiuyan-air.cn",
    ("web-8042", "fix", 0): "问「今年」却用 2025 搜索（今天是 2026-09-16）",
}

run("b10b", MANUAL)
