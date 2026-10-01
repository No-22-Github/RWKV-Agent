# DISTILL-CANARY-b4129d07 : distillation case
import json

case = json.load(open("case.json"))
entries = case["web_fixture"]

# The case's premise lives in the fixture: search advertises the notice page,
# but its fetch must fail so the date in its body is unreachable (v1.3 §2.3:
# a WebFixtureEntry error makes web_fetch return ok:false with that error
# text). Recompute both halves from the fixture itself.
target = None
healthy = None
for entry in entries:
    if entry.get("url_match") == "www.qinyashan.example/notice/ropeway-maintenance":
        target = entry
    if entry.get("url_match") == "www.qinyashan.example/park/hours":
        healthy = entry

if target is None or not target.get("error", "").startswith("Tavily extract failed"):
    raise SystemExit("fixture lacks the error entry for the ropeway notice page")
if healthy is None or healthy.get("error"):
    raise SystemExit("fixture lacks a healthy park-hours page for the retry leg")

# The date must not be leaked by the page a solver can still reach.
reached = healthy.get("content", "") + healthy.get("snippet", "")
for bait in ("2026-10-08", "10 月 8 日"):
    if bait in reached:
        raise SystemExit("fixture leaks the recovery date on the reachable page")

accepted = [
    "qinyashan.example",
    "qinyashan",
    "索道检修公告",
]
print(json.dumps({"expected_contains_any": accepted}))
