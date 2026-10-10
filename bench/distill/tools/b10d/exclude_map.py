#!/usr/bin/env python3
"""S5 reading verdicts for b10d (see tools/exclude_lib.py). Run from the repo root."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exclude_lib import run  # noqa: E402

LANG = "英文题用中文作答"
MANUAL = {
    ("code-8401", "orig", 0): LANG,
    ("code-8406", "orig", 0): LANG,
    ("log-8437", "orig", 0): LANG,
    ("log-8441", "orig", 0): LANG,
    ("log-8431", "orig", 0): "英文题用德文作答",
    # 数据里目标行被写成 ERROR 级别，老师据此答「没有成功记录」，与判据口径相反
    ("log-8440", "orig", 0): "目标行在数据里是 ERROR 级别，终答答「v12 从未发布成功」",
    ("log-8440", "orig", 2): "目标行在数据里是 ERROR 级别，终答答「v12 从未发布成功」",
    ("log-8442", "orig", 0): "目标行在数据里是 ERROR 级别，终答答「不是正常的成功收尾」",
    ("log-8442", "orig", 1): "目标行在数据里是 ERROR 级别，终答答「没有可信的成功完成行」",
    ("log-8417", "fix", 2): LANG,
    ("log-8419", "fix", 2): LANG,
    ("log-8419", "fix", 0): LANG,
    ("log-8421", "fix", 0): LANG,
    ("log-8429", "fix", 1): LANG,
    ("tab-8467", "fix", 1): LANG,
    ("log-8401", "fix", 0): "终答里冒出乱词「pista（依据）」",
    ("tab-8429", "fix", 1): "终答里自我更正「13 on Aug 2 or Aug 10... precisely 14」",
    ("tab-8430", "fix", 0): "终答把短日期说成 MM-DD-YYYY（README 是日-月-年）",
    ("tab-8433", "fix", 0): "终答凭空写「891 rows」",
    ("tab-8469", "fix", 2): "终答说「only three Ridge pickers」却只列两人",
    ("tab-8503", "fix", 2): "终答编出表里没有的「乙醇 / 甲醇」分项",
}
OVERSIZE = {
    ("log-8414", "fix", 1): "渲染后 13047 token，超过 8128 打包上限（整读日志）",
    ("log-8416", "fix", 2): "渲染后 13293 token，超过 8128 打包上限（整读日志）",
    ("log-8417", "fix", 1): "渲染后 14511 token，超过 8128 打包上限（整读日志）",
    ("log-8423", "fix", 0): "渲染后 15077 token，超过 8128 打包上限（整读日志）",
    ("log-8425", "fix", 1): "渲染后 15708 token，超过 8128 打包上限（整读日志）",
    ("log-8427", "fix", 0): "渲染后 13921 token，超过 8128 打包上限（整读日志）",
    ("log-8428", "fix", 0): "渲染后 14212 token，超过 8128 打包上限（整读日志）",
    ("tab-8401", "fix", 0): "渲染后 9007 token，超过 8128 打包上限（整读表格）",
    ("tab-8403", "fix", 1): "渲染后 10689 token，超过 8128 打包上限（整读表格）",
    ("tab-8403", "fix", 2): "渲染后 10810 token，超过 8128 打包上限（整读表格）",
    ("tab-8414", "fix", 0): "渲染后 8678 token，超过 8128 打包上限（整读表格）",
    ("tab-8416", "fix", 0): "渲染后 8835 token，超过 8128 打包上限（整读表格）",
    ("tab-8416", "fix", 2): "渲染后 9224 token，超过 8128 打包上限（整读表格）",
    ("tab-8423", "fix", 1): "渲染后 9016 token，超过 8128 打包上限（整读表格）",
    ("tab-8427", "fix", 1): "渲染后 8413 token，超过 8128 打包上限（整读表格）",
    ("tab-8432", "fix", 0): "渲染后 8565 token，超过 8128 打包上限（整读表格）",
    ("tab-8436", "fix", 2): "渲染后 9915 token，超过 8128 打包上限（整读表格）",
    ("tab-8438", "fix", 2): "渲染后 9817 token，超过 8128 打包上限（整读表格）",
}

run("b10d", MANUAL, OVERSIZE)
