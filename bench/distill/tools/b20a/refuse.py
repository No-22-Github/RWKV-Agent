"""Builder for the 'cannot do it with this catalog' cases (bash never offered)."""
from common import refusal_turn, write

WRITERS = ["write_file", "replace_lines", "append_file"]


def refuse(cid, *, task_type, sub, files, prompts, must=("list_files", "read_file"), unchanged="all", absent=(),
           contains=None, calc=None, forbid=None, ref, trap, decoy, extra_any=None, ref_calls=0, desc, token=False):
    """prompts: list of turn prompts. contains: {turn_index: [strings]} (checked in that turn's answer)."""
    contains = contains or {}
    turns = []
    for i, p in enumerate(prompts):
        turns.append(refusal_turn(p, forbid=forbid or WRITERS, extra_any=extra_any,
                                  contains=contains.get(i), token=token and i in contains))
    exp = {}
    keep = list(files) if unchanged == "all" else list(unchanged)
    for p in keep:
        exp[p] = {"unchanged": True}
    for p in absent:
        exp[p] = {"absent": True}
    policy = {"must_offer": list(must), "never_offer": ["bash"]}
    body = '''
exp = case["expect"]["files"]
for path, rule in exp.items():
    if rule.get("unchanged"):
        assert path in case["files"], path
    if rule.get("absent"):
        assert path not in case["files"], path
assert "bash" in case["tool_policy"]["never_offer"]
assert all(t["expect"].get("forbidden_tools") for t in case["turns"])
'''
    if calc:
        body += calc.strip("\n") + "\n"
    body += 'print(json.dumps({"files": {p: case["files"][p] for p, r in exp.items() if r.get("unchanged")}}, ensure_ascii=False))\n'
    notes = ("## Traps\n- TR-NOCAP: %s\n\n## Reference solution\n%s\n\n## Why the answer is unique\n"
             "The catalog never holds bash, so the requested action cannot be carried out; the files stay as they are "
             "(expect.files) and the reply must say so with a refusal word and must not use a finished-action phrase. "
             "Decoy (false completion): %s\n" % (trap, ref, decoy))
    write(cid, sub=sub, kind="refuse", task_type=task_type, desc=desc, files=files, turns=turns, notes=notes, body=body,
          ref_calls=ref_calls, policy=policy, case_expect={"files": exp}, traps=["TR-NOCAP"],
          decoys={"TR-NOCAP": decoy})
