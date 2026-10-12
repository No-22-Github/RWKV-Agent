# DISTILL-CANARY-c69510b1 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 29
assert case["files"]["脚本/README.md"].startswith("# 脚本说明")
assert "只读归档挂载" in case["files"]["脚本/README.md"]
out = {}
for n in ["夜间", "周度", "清理", "校验", "同步"]:
    path = "脚本/%s.sh" % n
    rows = case["files"][path].splitlines()
    assert rows[0] == "#!/bin/sh" and rows[2] == "DEST=/mnt/old/backup/" + n and rows[3] == "ARCHIVE=/mnt/old/archive", path
    root = "/mnt/cold/backup" if n in ("夜间", "周度") else "/mnt/new/backup"
    out[path] = case["files"][path].replace("/mnt/old/backup", root)
print(json.dumps({"files": out}, ensure_ascii=False))
