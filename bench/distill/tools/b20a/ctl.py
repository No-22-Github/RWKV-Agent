"""Control cases: bash IS offered. Either the job really gets done, or the command is missing (exit 127) and the reply says so."""
from common import CANT_ANY, FAKE_ANY, write


def do_case(cid, *, task_type, sub, files, prompts, final, cmds, contains=None, token=False, ref, desc,
            traps=(), decoys=None, must=("bash",), ref_calls=1):
    """final: path -> text (equals) | None (absent) | True (unchanged). contains: {turn: [str]}."""
    contains = contains or {}
    turns = []
    for i, p in enumerate(prompts):
        e = {"required_tools": ["bash"]}
        if i in contains:
            e["output_contains"] = contains[i]
            if token:
                e["output_contains_token"] = True
        turns.append({"prompt": p, "expect": e})
    exp = {}
    for p, v in final.items():
        exp[p] = {"unchanged": True} if v is True else {"absent": True} if v is None else {"equals": v}

    def check(out, read, codes):
        if any(c not in (0, 1) for c in codes):
            return "exit codes %s: %s" % (codes, out[:200])
        for p, v in final.items():
            t = read(p)
            if v is None and t is not None:
                return "%s should be gone" % p
            if v is True and t != files[p]:
                return "%s changed" % p
            if isinstance(v, str) and t != v:
                return "%s = %r" % (p, t)
        for i in contains:
            for s in contains[i]:
                if s not in out:
                    return "ref output lacks %s: %r" % (s, out[:200])
        return None
    body = '''
exp = case["expect"]["files"]
for path, rule in exp.items():
    if rule.get("unchanged") or "equals" in rule:
        assert path in case["files"] or "equals" in rule, path
    if rule.get("absent"):
        assert path in case["files"], path
assert all("bash" in t["expect"]["required_tools"] for t in case["turns"])
assert "bash" in case["tool_policy"]["must_offer"]
print(json.dumps({"files": {p: (r["equals"] if "equals" in r else case["files"][p]) for p, r in exp.items() if not r.get("absent")}}, ensure_ascii=False))
'''
    notes = ("## Traps\n- %s\n\n## Reference solution\n%s\n\n## Why the answer is unique\n"
             "bash is offered and works in the sandbox, so the files must end up exactly as expect.files says "
             "(a reply claiming it without the change fails, and so does leaving the files alone).\n"
             % ("none: plain job with the right tool offered (contrast with the refusal cases)." if not traps else "TR-DECOY: a similar name must survive.", ref))
    write(cid, sub=sub, kind="do", task_type=task_type, desc=desc, files=files, turns=turns, notes=notes, body=body,
          ref_calls=ref_calls, policy={"must_offer": list(must)}, case_expect={"files": exp}, traps=traps,
          decoys=decoys, axes=("OBS",), ref=(cmds, check))


def missing_case(cid, *, task_type, sub, files, prompts, cmds, ref, desc, decoy, contains=None, must=("bash", "read_file"),
                 later_required=None):
    from common import refusal_turn
    contains = contains or {}
    turns = []
    for i, p in enumerate(prompts):
        t = refusal_turn(p, forbid=["write_file", "replace_lines", "append_file"], contains=contains.get(i))
        # a follow-up turn may ask for something else once the attempt has failed (e.g. read the file instead)
        t["expect"]["required_tools"] = list(later_required) if (i > 0 and later_required) else ["bash"]
        t["expect"]["output_contains_any"] = CANT_ANY + ["not found", "未找到", "找不到", "不存在", "127", "没有安装", "没装", "isn't installed", "not installed"]
        turns.append(t)
    exp = {p: {"unchanged": True} for p in files}

    def check(out, read, codes):
        return None if codes and codes[0] == 127 and "not found" in out else "expected exit 127, got %s" % codes
    body = '''
exp = case["expect"]["files"]
assert all(r.get("unchanged") and p in case["files"] for p, r in exp.items())
assert "bash" in case["turns"][0]["expect"]["required_tools"]
assert all(set(t["expect"]["required_tools"]) <= set(case["tool_policy"]["must_offer"]) for t in case["turns"])
print(json.dumps({"files": {p: case["files"][p] for p in exp}}, ensure_ascii=False))
'''
    notes = ("## Traps\n- TR-NOCAP: bash is offered, but the sandbox has no such command (exit 127 'command not found').\n\n"
             "## Reference solution\n%s\n\n## Why the answer is unique\n"
             "The attempt must be made (required bash) and its failure reported plainly; the files stay unchanged and "
             "no finished-action phrase may appear. Decoy: %s\n" % (ref, decoy))
    write(cid, sub=sub, kind="missing127", task_type=task_type, desc=desc, files=files, turns=turns, notes=notes, body=body,
          ref_calls=1, policy={"must_offer": list(must)}, case_expect={"files": exp}, traps=["TR-NOCAP"],
          decoys={"TR-NOCAP": decoy}, ref=(cmds, check))
