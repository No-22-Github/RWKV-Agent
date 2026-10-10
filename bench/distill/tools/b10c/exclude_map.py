#!/usr/bin/env python3
"""S5 reading verdicts for b10c (see tools/exclude_lib.py). Run from the repo root."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exclude_lib import run  # noqa: E402

MANUAL = {
    ("cfg-8203", "orig", 1): "终答把 README 写成「READM E」（词中断开的乱码）",
    ("fs-8209", "orig", 1): "终答开头泄漏自言自语「Pruning? That's Lena too probably.」",
    ("fs-8206", "orig", 1): "英文题用中文作答",
    ("nt-8212", "orig", 0): "终答末句不通（「按常见口径不足 8 小时或 6 小时整，也不算跨日」）",
    # 题面没提 DONE，终答却说「不做 DONE / can't confirm DONE」：老师把附加指令里的口径带进了回答
    ("log-8204", "fix", 1): "题面没要求 DONE，终答却说「因此也不写 DONE」",
    ("log-8219", "fix", 0): "题面没要求 DONE，终答却说「can't confirm DONE」",
    ("tab-8202", "fix", 0): "题面没要求 DONE，终答却说「不做 DONE」",
    ("tab-8204", "fix", 1): "题面没要求 DONE，终答却说「也没有 DONE」",
    ("tab-8206", "fix", 2): "题面没要求 DONE，终答却说「也不能说 DONE」",
    ("tab-8215", "fix", 1): "题面没要求 DONE，终答却说「there is no DONE」",
}
OVERSIZE = {
    ("log-8200", "fix", 0): "渲染后 13816 token，超过 8128 打包上限（整读日志 jsonl）",
    ("log-8203", "fix", 0): "渲染后 8198 token，超过 8128 打包上限（整读日志 jsonl）",
    ("log-8204", "fix", 2): "渲染后 14383 token，超过 8128 打包上限（整读日志 jsonl）",
    ("log-8208", "fix", 1): "渲染后 9416 token，超过 8128 打包上限（整读日志 jsonl）",
    ("log-8208", "fix", 2): "渲染后 9476 token，超过 8128 打包上限（整读日志 jsonl）",
    ("log-8210", "fix", 1): "渲染后 14613 token，超过 8128 打包上限（整读日志 jsonl）",
    ("log-8210", "fix", 0): "渲染后 14786 token，超过 8128 打包上限（整读日志 jsonl）",
    ("log-8215", "fix", 1): "渲染后 10727 token，超过 8128 打包上限（整读日志 jsonl）",
    ("log-8216", "fix", 0): "渲染后 13437 token，超过 8128 打包上限（整读日志 jsonl）",
    ("log-8216", "fix", 1): "渲染后 14659 token，超过 8128 打包上限（整读日志 jsonl）",
}

run("b10c", MANUAL, OVERSIZE)
