# DISTILL-CANARY-e4794f29 : distillation case
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
    if entry.get("url_match") == "www.gallowmere.example/notices/branch-move":
        target = entry
    elif entry.get("url_match") == "www.gallowmere.example/branches":
        healthy = entry

if target is None or not target.get("error", "").startswith("Tavily extract failed"):
    raise SystemExit("fixture lacks the error entry for the notice page")
if healthy is None or healthy.get("error"):
    raise SystemExit("fixture lacks a healthy companion page for the retry leg")
if "branch notices page" not in healthy.get("content", ""):
    raise SystemExit("fixture guard failed: the healthy page lost its pointer to the notice")

# The value must not be leaked by anything a solver can reach.
dumped = json.dumps(entries, ensure_ascii=False)
for bait in ['November 9', '2026-11-09']:
    if bait in dumped:
        raise SystemExit("fixture leaks " + bait + "; the value must be unreachable")

accepted = ['gallowmere.example', 'gallowmere', 'branch relocation', 'relocation notice']
print(json.dumps({"expected_contains_any": accepted}))
