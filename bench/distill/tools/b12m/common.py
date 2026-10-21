"""b12m (v1.41 first scale batch: bash + get_weather on agent-tool-v2.0) settings; the
writer, fixture helpers and sidecar client are ../casegen.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch, Sidecar, check_reference, lines, weather  # noqa: E402,F401

write_case = Batch(salt="b12m", author="llm:claude-sonnet-5-5-b12m", version="v1.41",
                   tool_catalog="agent-tool-v2.0").write_case

import json  # noqa: E402


def files_check(rules, originals):
    """Reference check for edit cases: rules maps path -> {"equals": text} | {"unchanged": True} | {"absent": True}."""
    def check(_out, root):
        for path, rule in rules.items():
            full = os.path.join(root, path)
            if rule.get("absent"):
                if os.path.exists(full):
                    return "%s should be gone" % path
                continue
            if not os.path.exists(full):
                return "%s missing" % path
            want = rule["equals"] if "equals" in rule else originals[path]
            text = open(full, encoding="utf-8").read()
            if text != want:
                return "%s = %r" % (path, text[:200])
        return None
    return check


def rules_for(files, final):
    out = {}
    for path, text in files.items():
        if path not in final:
            out[path] = {"absent": True}
        elif final[path] == text:
            out[path] = {"unchanged": True}
        else:
            out[path] = {"equals": final[path]}
    for path, text in final.items():
        if path not in files:
            out[path] = {"equals": text}
    return out


def has(*needles):
    return lambda out, _root: None if all(n in out for n in needles) else "ref stdout %r lacks %s" % (out[:200], needles)


def thousands(value):
    whole, _, frac = str(value).partition(".")
    grouped = f"{int(whole):,}" + ("." + frac if frac else "")
    return [str(value)] if grouped == str(value) else [str(value), grouped]


def phrasings(*items):
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, t) for i, t in enumerate(items))


HEAD = 'import json\ncase = json.load(open("case.json"))\n'


def verify_src(files, body):
    """verify.py source: loads the case, pins the total fixture line count (so deleting any fixture line breaks
    it), then runs body."""
    total = sum(len(t.splitlines()) for t in files.values())
    return HEAD + 'assert sum(len(t.splitlines()) for t in case["files"].values()) == %d\n' % total + body.strip("\n") + "\n"


DONE = {"output_contains": ["DONE"], "max_output_chars": 600}
