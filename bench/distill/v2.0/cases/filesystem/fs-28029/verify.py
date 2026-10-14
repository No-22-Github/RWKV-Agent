# DISTILL-CANARY-0d55b897 : distillation case
import json
import re

case = json.load(open("case.json"))
f = case["files"]
assert f["README.md"].startswith("园务通知")
assert f["通知/伙食/十月带量食谱.md"].startswith("十月带量食谱")
assert f["通知/活动/秋游安排.md"].startswith("秋游安排")
assert f["通知/体检/秋季体检安排.md"].startswith("秋季体检安排")
m = re.search(r"(\d+)\s*月\s*(\d+)\s*日", f["通知/体检/秋季体检安排.md"])
assert m and m.group(1) == "10"
d = "10 月 %s 日" % m.group(2)
ask = ["哪个目录", "哪条路径", "哪个路径", "放在哪", "目录路径", "所在的目录", "所在目录", "具体路径", "完整路径"]
print(json.dumps({"expected_contains_any": ask + [d, d.replace(" ", ""), "2026-10-%s" % m.group(2)]},
                 ensure_ascii=False))
