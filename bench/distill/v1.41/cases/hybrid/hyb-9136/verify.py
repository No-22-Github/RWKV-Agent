# DISTILL-CANARY-84b64df3 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 5
path = "出游/天气表.md"
rows = case["files"][path].splitlines()
assert rows[:2] == ["# 出游天气表", ""] and rows[3] == "| --- | --- | --- | --- |" and len(rows) == 5
qd, dl = (f["report"]["daily"] for f in case["weather_fixture"])
assert qd[1]["date"] == "2026-09-17" and dl[2]["date"] == "2026-09-18"
def row(d, city):
    low, high = d["temp_c"].split("~")
    return "| %s | %s | %s | %s~%s°C |" % (d["date"][5:], city, d["condition"], low, high)
rows += [row(qd[1], "青岛"), row(dl[2], "大连")]
print(json.dumps({"files": {path: chr(10).join(rows) + chr(10)}}, ensure_ascii=False))
