"""b12n (v1.41 first scale batch: bash + get_weather on work-v2) settings; the
writer, fixture helpers and sidecar client are ../casegen.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch, Sidecar, check_reference, lines, weather  # noqa: E402,F401

write_case = Batch(salt="b12n", author="llm:claude-sonnet-5-5-b12n", version="v1.41",
                   tool_catalog="work-v2").write_case

import json  # noqa: E402
import re  # noqa: E402
from random import Random  # noqa: E402


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
                return "%s = %r (want %r)" % (path, text[:300], want[:300])
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


def phrasings(*items):
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, t) for i, t in enumerate(items))


DONE = {"output_contains": ["DONE"], "max_output_chars": 600}


def ts(i):
    return "2026-10-%02d %02d:%02d:%02d" % (1 + i % 7, (i * 5) % 24, (i * 7) % 60, (i * 13) % 60)


def literal_free(files, answers):
    """Numeric answers must not appear as a token in the fixture, so the sabotage test cannot corrupt an unrelated number."""
    text = "\n".join(files.values())
    for ans in answers:
        for s in (ans or {}).get("any", []):
            if re.search(r"(?<![0-9])%s(?![0-9])" % re.escape(s), text):
                return False
    return True


def chain_case(refs, cid, *, desc, task_type, family, level="L3", gen, logic, prompts, cmds, traps, trap_note, alts, decoys=None,
               axes=("OBS", "CHN", "CON")):
    """A multi-turn case: lookups (answer in the reply) and edits (files change). logic is Python source defining
    solve(files) -> (answers, final_files, info); answers has one entry per turn: {"any": [...]} | {"all": [...]} | None.
    cmds(info) -> one list of reference bash commands per turn. The same logic runs inside verify.py."""
    base = int(cid.split("-")[1])
    ns = {}
    exec(logic, ns)
    for seed in range(500):
        files = gen(Random(base + seed * 7919))
        answers, final, info = ns["solve"](files)
        if literal_free(files, answers):
            break
    else:
        raise SystemExit(cid + ": no seed gives a fixture without literal answers")
    assert len(answers) == len(prompts), cid
    turn_cmds = cmds(info)
    assert len(turn_cmds) == len(prompts), cid
    flat = [c for t in turn_cmds for c in t]
    rules = rules_for(files, final)
    expects = []
    for ans in answers:
        if ans is None:
            expects.append(dict(DONE))
        elif "any" in ans:
            expects.append({"output_contains_any": ans["any"], "max_output_chars": 600})
        else:
            expects.append({"output_contains": ans["all"], "max_output_chars": 600})
    total = sum(len(t.splitlines()) for t in files.values())
    body = ('assert sum(len(t.splitlines()) for t in case["files"].values()) == %d\n' % total + logic.strip("\n") + "\n"
            'files = case["files"]\n'
            'answers, final, info = solve(files)\n'
            'for turn, ans in zip(case["turns"], answers):\n'
            '    if ans is None:\n'
            '        continue\n'
            '    if "any" in ans:\n'
            '        assert turn["expect"]["output_contains_any"] == ans["any"], (turn["expect"], ans)\n'
            '    else:\n'
            '        assert turn["expect"]["output_contains"] == ans["all"], (turn["expect"], ans)\n'
            'out = {p: t for p, t in final.items() if files.get(p) != t}\n'
            'print(json.dumps({"files": out}, ensure_ascii=False))\n')
    verify = 'import json\ncase = json.load(open("case.json"))\n' + body
    steps = ""
    for i, (p, c) in enumerate(zip(prompts, turn_cmds)):
        steps += "Turn %d (%s):\n" % (i + 1, "answer in the reply" if answers[i] else "edit, reply DONE")
        steps += "".join("%d. bash: `%s`\n" % (j + 1, x) for j, x in enumerate(c))
    notes = f"""## Traps
{trap_note}
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
{steps}
## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).
""" + phrasings(*alts)
    refs[cid] = (files, flat, files_check(rules, files))
    return write_case(
        cid, desc=desc, task_type=task_type, family=family, level=level, ref_calls=len(flat), traps=traps,
        decoys=decoys or {t: None for t in traps}, axes=list(axes), files=files, verify=verify, notes=notes,
        case_expect={"files": rules}, turns=[{"prompt": p, "expect": e} for p, e in zip(prompts, expects)])
