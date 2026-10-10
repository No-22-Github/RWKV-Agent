#!/usr/bin/env python3
"""S5 reading verdicts for b10e (see tools/exclude_lib.py). Run from the repo root."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exclude_lib import run  # noqa: E402

LANG = "英文题用中文作答"
NODONE = "题面没要求 DONE，终答却写了 DONE"
MANUAL = {
    ("cfg-8651", "orig", 0): LANG,
    ("code-8604", "orig", 0): LANG,
    ("scr-8030", "orig", 2): LANG,
    ("scr-8013", "orig", 1): "中文题用英文作答",
    ("cfg-8655", "orig", 2): "英文题用中文作答，且把路径写成 .bssh",
    ("cfg-8680", "orig", 0): "英文题用法文作答",
    ("cfg-8634", "orig", 0): NODONE,
    ("cfg-8690", "orig", 0): NODONE,
    ("code-8600", "orig", 0): NODONE,
    ("scr-8021", "orig", 2): NODONE,
    ("cfg-8638", "orig", 2): "两次 replace_lines 后又用 write_file 整体覆盖，路径凌乱",
    ("cfg-8646", "orig", 0): "DONE 写在终答开头而不是末尾",
    ("cfg-8658", "orig", 1): "终答补充说明自相矛盾（「Restart=always 手动 stop 后也会重启，可用 systemctl stop 不受影响」）",
    ("doc-8602", "orig", 1): "反复改了四次才改对，路径凌乱",
    ("scr-8006", "orig", 1): "预测输出算错（东门站 1250+780+4000 克写成 8.03 kg）",
    ("scr-8007", "orig", 1): "终答前后矛盾（「that's miles→km only roughly, actually the old value was wrong」）",
    ("scr-8020", "orig", 2): "预测输出算错（可见数据里 zhangsan 刷卡 3 次，写成 2）",
    ("hyb-8601", "fix", 0): "官网公告 10 月 15 日才生效（今天 9 月 16 日），改了值又附加保留，与「改成现行价」不符",
    ("hyb-8601", "fix", 2): "官网公告 10 月 15 日才生效（今天 9 月 16 日），改了值又附加保留，与「改成现行价」不符",
    ("hyb-8603", "fix", 1): "拿「上海 2025」和凭空的数字 36921 去搜索",
}

run("b10e", MANUAL)
