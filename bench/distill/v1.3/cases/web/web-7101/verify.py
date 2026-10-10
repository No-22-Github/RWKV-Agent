# DISTILL-CANARY-c58d3a72 : distillation case
import json

case = json.load(open("case.json"))
entries = case["web_fixture"]

# The case's premise lives in the fixture: search advertises the reference
# page, but its fetch must fail so the value documented on it is unreachable
# (v1.3 §2.3: a WebFixtureEntry error makes web_fetch return ok:false with
# that error text). Recompute both halves from the fixture itself.
target = None
healthy = None
for entry in entries:
    if entry.get("url_match") == "docs.osterlin.example/datasink/data-sink-reference":
        target = entry
    if entry.get("url_match") == "docs.osterlin.example/datasink/quickstart":
        healthy = entry

if target is None or not target.get("error", "").startswith("Tavily extract failed"):
    raise SystemExit("fixture lacks the error entry for the data-sink reference")
if healthy is None or healthy.get("error"):
    raise SystemExit("fixture lacks a healthy quickstart page for the retry leg")

# The value must not be leaked by the pages a solver can still reach.
if "seconds" in healthy.get("content", "") or "seconds" in healthy.get("snippet", ""):
    raise SystemExit("fixture leaks a flush interval on the reachable page")

accepted = [
    "osterlin",
    "Osterlin",
    "data-sink reference",
]
print(json.dumps({"expected_contains_any": accepted}))
