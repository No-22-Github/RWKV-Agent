# DISTILL-CANARY-125af4f6 : distillation case
import json
import re

case = json.load(open("case.json"))
f = case["files"]
classes = ["小班", "中班", "大班", "托班"]
dates = {}
for cls in classes:
    body = f["家园/联系册/%s-十月.md" % cls]
    assert body.splitlines()[0].startswith(cls), cls
    m = re.search(r"最后更新：(\d{4}-\d{2}-\d{2})", body)
    assert m, cls
    dates[cls] = m.group(1)
chosen = [c for c in classes if c in case["turns"][1]["prompt"]]
assert len(chosen) == 2, chosen
assert len(set(dates.values())) == 4, dates
latest = max(chosen, key=lambda c: dates[c])
assert latest == "托班" and dates[latest] == "2026-10-13", (latest, dates)
d = dates[latest]
parts = d.split("-")
ask = ["哪两个班", "哪几个班", "哪两个班级", "哪些班", "班级名称", "班的名称", "班级编号"]
print(json.dumps({"expected_contains_any": ask +
                  ["%s 月 %s 日" % (int(parts[1]), int(parts[2])),
                   "%s月%s日" % (int(parts[1]), int(parts[2])), d,
                   "%s-%s" % (parts[1], parts[2])]}, ensure_ascii=False))
