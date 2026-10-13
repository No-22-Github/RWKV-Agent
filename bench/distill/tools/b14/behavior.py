#!/usr/bin/env python3
"""S5 behavior labels for b14 (v1.42) teacher runs.

    python3 bench/distill/tools/b14/behavior.py <run-dir> [<run-dir> ...] [--report out.tsv] [--json out.json]

Reuses ../b12/behavior.py (covered / ordinary / reject / fail, the shared
problems and the b12 kinds) unchanged, adds the b14 case specs from
specs.json (written by build.py) and four kinds b12 did not have:

  ask_then_run          turn 1 asks for a command only (no call allowed), turn 2
                        asks to run it: covered when a turn-2 bash result shows
                        the answer
  weather_switch        every turn names its own city: covered when each turn
                        has a successful get_weather for that turn's city
  weather_unknown       the place is not in the fixture: covered when a
                        get_weather call for it came back `location not found`
                        (the final wording is the scorer's job); a successful
                        lookup of some other place presented as it is a reject
  concept_then_weather  turn 1 is a concept question (no call), turn 2 needs a
                        forecast covering the asked date
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("b12_behavior", os.path.join(HERE, "..", "b12", "behavior.py"))
B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B)

with open(os.path.join(HERE, "specs.json"), encoding="utf-8") as f:
    _b14 = json.load(f)
_clash = set(B.SPEC) & set(_b14)
if _clash:
    sys.exit("b14 specs redefine %s" % ", ".join(sorted(_clash)))
B.SPEC.update(_b14)


def check_ask_then_run(turns, spec, case):
    problems = []
    if turns[0][0]:
        problems.append("ask_then_run: turn 1 made %d call(s)" % len(turns[0][0]))
    want = B.literals(case["turns"][-1]["expect"])
    hit = any(c.tool == "bash" and all(B.has_literal(c.text, w) for w in want) for c in turns[-1][0])
    return hit and not problems, problems


def _named(call, names):
    loc = (call.args.get("location") or "").lower()
    return any(n.lower() in loc or (loc and loc in n.lower()) for n in names)


def check_weather_switch(turns, spec, case):
    ok = True
    for (calls, _), names in zip(turns, spec["cities"]):
        ok = ok and any(c.tool == "get_weather" and not c.error and _named(c, names) for c in calls)
    return ok, []


def check_weather_unknown(turns, spec, case):
    calls = [c for t in turns for c in t[0] if c.tool == "get_weather"]
    missing = spec["missing"]
    asked = any(c.error and "location not found" in c.error and missing.lower() in (c.args.get("location") or "").lower() for c in calls)
    known = spec.get("known") or []
    substitutes = [c for c in calls if not c.error and not _named(c, known)]
    problems = ["weather_unknown: answered from %s instead" % c.args.get("location") for c in substitutes]
    return asked, problems


def check_concept_then_weather(turns, spec, case):
    problems = []
    if turns[0][0]:
        problems.append("concept_then_weather: turn 1 made %d call(s)" % len(turns[0][0]))
    covered, more = B.check_weather(turns[1:], spec, case)
    return covered and not problems, problems + more


B.CHECKS.update({
    "ask_then_run": check_ask_then_run,
    "weather_switch": check_weather_switch,
    "weather_unknown": check_weather_unknown,
    "concept_then_weather": check_concept_then_weather,
})

if __name__ == "__main__":
    B.main()
