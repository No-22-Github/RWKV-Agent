# DISTILL-CANARY-2a9d73f6 : p13 holdout (eval-only)
import json

case = json.load(open("case.json", encoding="utf-8"))
sept = case["files"]["logs/handoff-2026-09.txt"]
aug = case["files"]["logs/handoff-2026-08.txt"]
entry = "2026-09-29 晚班 陈默：3 号库烟雾报警器误报，已复位，报修单 SD-2143。"
print(json.dumps({"files": {
    "logs/handoff-2026-09.txt": sept + entry + "\n",
    "logs/handoff-2026-08.txt": aug,
}}))
