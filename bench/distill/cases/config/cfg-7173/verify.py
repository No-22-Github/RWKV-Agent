# DISTILL-CANARY-9db92d9c : distillation case

import json

case = json.load(open("case.json"))
instance = json.loads(case["files"]["config/live-classroom.json"])
defaults = json.loads(case["files"]["config/liveclass-defaults.json"])

KEY = "live_poll_interval_ms"

# README.md: the instance config overrides the defaults and an unset key falls
# through to the profile; a key in neither layer has no effective value.
effective = dict(defaults)
effective.update(instance)
if KEY in effective:
    raise SystemExit("fixture defines " + KEY + "; the absent-key case is broken")

# Positive control: the neighbouring key the decoy figure comes from.
if effective.get("chat_flush_interval_ms") != 800:
    raise SystemExit("fixture guard failed: chat_flush_interval_ms decoy is broken")

accepted = [
    "live_poll_interval_ms",
    "live poll interval",
    "轮询间隔",
]
print(json.dumps({"expected_contains_any": accepted}))
