# DISTILL-CANARY-7b8e2112 : p13 holdout eval case (eval-only, never for training)
#
# 判据是缺失汇报（output_contains_any + output_excludes），没有可独立重算的值，
# 本脚本只回显夹具快照：条款总览与各条款主题。
import json
import re

case = json.load(open("case.json"))
text = case["files"]["报销制度.md"]
clauses = re.findall(r"^- (第 \d+ 条 .+)$", text, re.M)
snapshot = {
    "clause_index": clauses,
    "covers_client_entertainment": any(("招待" in c or "宴请" in c) for c in clauses),
}
print(json.dumps(snapshot, ensure_ascii=False))
