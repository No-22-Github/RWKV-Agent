# DISTILL-CANARY-44f0b100 : p13 holdout eval case (eval-only, never for training)
#
# 判据是自然语言缺失汇报（output_contains_any + output_excludes），没有可独立重算的值，
# 本脚本只回显夹具快照：核对订单表与字段字典的一致性。
import csv
import io
import json

case = json.load(open("case.json"))
orders = csv.DictReader(io.StringIO(case["files"]["orders/订单明细-2026-09.csv"]))
order_cols = [c.strip() for c in orders.fieldnames or []]
dic = csv.DictReader(io.StringIO(case["files"]["字段字典.csv"]))
enabled = [r["字段"].strip() for r in dic if r["状态"].strip() == "启用"]
disabled = [r["字段"].strip() for r in dic if r["状态"].strip() == "停用"]
snapshot = {
    "order_columns": order_cols,
    "enabled_fields": enabled,
    "disabled_fields": disabled,
    "order_row_count": sum(1 for _ in orders),
}
print(json.dumps(snapshot, ensure_ascii=False))
