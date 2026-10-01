# DISTILL-CANARY-9f00cafa : distillation case
import json

case = json.load(open("case.json"))
entries = case["web_fixture"]

TARGET = 'docs.kelterby.example/switchgear/api-reference'
FALLBACK = 'docs.kelterby.example/switchgear/quickstart'
DECOY = '600'

target = fallback = None
for e in entries:
    if e.get("url_match") == TARGET:
        target = e
    if e.get("url_match") == FALLBACK:
        fallback = e

# The case's premise lives in the fixture: search advertises the target
# page, but its fetch must fail so the value documented on it is
# unreachable (v1.3 §2.3: a WebFixtureEntry error makes web_fetch return
# ok:false with that error text).
if target is None or not target.get("error", "").startswith("Tavily extract failed"):
    raise SystemExit("fixture lacks the error entry for the target page")
if fallback is None or fallback.get("error"):
    raise SystemExit("fixture lacks a healthy fallback page for the retry leg")


# Neither the value nor the decoy may leak through any surface a solver
# can see (snippets included).
for e in entries:
    for field in ("snippet", "content"):
        if DECOY in e.get(field, ""):
            raise SystemExit("fixture leaks the decoy on a reachable surface")

accepted = ['kelterby.example', 'kelterby', 'API reference']
print(json.dumps({"expected_contains_any": accepted}))
