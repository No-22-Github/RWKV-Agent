# DISTILL-CANARY-c032a4f6 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {"备份/db-2026-09-10.sql.gz": "placeholder\n", "备份/db-2026-09-11.sql.gz": "placeholder\n", "备份/db-2026-09-12.sql.gz": "placeholder\n"}
print(json.dumps({"expected_contains_any": ["-mtime +7", "-mtime", "-delete"]}, ensure_ascii=False))
