# DISTILL-CANARY-a9a38e88 : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
entries = case["web_fixture"]

# The case's premise lives in the fixture: search advertises the
# notice page, but its fetch must fail so the value in its body is
# unreachable (v1.3 §2.3: a WebFixtureEntry error makes web_fetch
# return ok:false with that error text).
target = None
healthy = None
for entry in entries:
    if entry.get("url_match") == "www.cangyu.example/notice/sail-resume":
        target = entry
    elif entry.get("url_match") == "www.cangyu.example/fares":
        healthy = entry

if target is None or not target.get("error", "").startswith("Tavily extract failed"):
    raise SystemExit("fixture lacks the error entry for the notice page")
if healthy is None or healthy.get("error"):
    raise SystemExit("fixture lacks a healthy companion page for the retry leg")
if "以停航恢复公告页发布为准" not in healthy.get("content", ""):
    raise SystemExit("fixture guard failed: the healthy page lost its pointer to the notice")

# The value must not be leaked by anything a solver can reach.
dumped = json.dumps(entries, ensure_ascii=False)
for bait in ['06:30', '6 点 30 分']:
    if bait in dumped:
        raise SystemExit("fixture leaks " + bait + "; the value must be unreachable")

accepted = ['cangyu.example', 'cangyu', '停航恢复公告']
print(json.dumps({"expected_contains_any": accepted}))
