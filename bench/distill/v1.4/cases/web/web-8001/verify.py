# DISTILL-CANARY-4d9ac7e4 : distillation case
import json

case = json.load(open("case.json"))
pages = {w["url"]: w for w in case["web_fixture"]}
assert pages["https://lumenroute.io/pricing"]["error"].startswith("Connection timed out")
status = pages["https://status.lumenroute.io/"]["content"]
assert "/pricing" in status and "console.lumenroute.io" in status
words = ["timed out", "timing out", "time out", "timeout", "couldn't load", "could not load",
         "unable to load", "couldn't fetch", "could not fetch", "unable to fetch", "failed to load"]
print(json.dumps({"expected_contains_any": words}))
