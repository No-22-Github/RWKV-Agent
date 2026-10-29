"""b23c (v2.3: missing key information -> ask first; C0 controls -> just do it) shared settings."""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch  # noqa: E402

BATCH = Batch(salt="b23c", author="llm:claude-sonnet-b23c", version="v2.3", tool_catalog="agent-tool-v3.2")
META = {}

# Phrases that signal "I am asking you something". Matching is case-folded for Latin
# letters (see Expectation docs), so one spelling each; "?" and the full-width "？"
# catch any real question. Phrases are specific enough not to appear in a plain report.
ASK = ["?", "？",
       "请问", "请告诉", "请确认", "请说明", "请指明", "请提供", "请回复", "请先告诉", "麻烦告诉", "麻烦确认", "麻烦说明", "麻烦提供",
       "需要你", "需要您", "需要先确认", "先确认", "确认一下", "跟我确认", "和我确认",
       "哪一个", "哪个", "哪份", "哪些", "哪套", "哪种", "哪条", "哪张", "哪台", "哪项", "哪边", "哪位", "哪天", "哪组",
       "你指的是", "你是指", "您指的是", "您是指", "指的是哪", "是指哪", "想改哪", "要改哪", "想让我改", "要我改",
       "能告诉我", "可以告诉我", "能否告诉", "能不能告诉", "能否提供", "可以提供", "还是要", "还是改", "还是只", "还是都",
       "which one", "which of", "which file", "which environment", "which service", "which config", "which template", "which version",
       "which address", "which rate", "which person", "which team", "which date", "which copy", "which report", "which export",
       "do you want", "would you like", "should i ", "shall i ", "did you mean", "do you mean", "want me to",
       "could you tell", "could you confirm", "could you clarify", "could you specify", "could you provide", "could you let me know",
       "can you tell", "can you confirm", "can you clarify", "can you specify", "can you provide", "can you let me know",
       "please tell", "please confirm", "please specify", "please clarify", "please provide", "please let me know",
       "let me know", "need to know", "need you to", "need a bit more", "need more information", "before i change", "before i edit",
       "before i make", "before i go", "before i proceed", "before making", "before editing", "before changing", "clarify", "confirm"]

# Replies that claim the edit already happened. Case-sensitive, kept to first-person
# completions so "I have not changed anything" and "尚未修改" are not caught.
DONE_BAD = ["我已修改", "我已经修改", "我已更新", "我已经更新", "我已将", "我已经将", "我已改", "我已经改", "已帮你改", "已为你改", "已帮您改",
            "已为您改", "已帮你修改", "已为你修改", "已帮你更新", "已为你更新", "已成功修改", "已成功更新", "修改成功", "更新成功", "已改好",
            "已经改好", "已设置为", "已经设置为", "已改为", "已经改为", "已替换", "已经替换", "已删除", "已经删除", "删除成功", "已重命名",
            "已经重命名", "重命名成功", "已写入", "已经写入", "已填入", "已经填入", "已按", "已经按",
            "I changed", "I've changed", "I’ve changed", "I have changed", "I updated", "I've updated", "I’ve updated", "I have updated",
            "I edited", "I've edited", "I’ve edited", "I have edited", "I modified", "I've modified", "I’ve modified", "I set ", "I've set",
            "I’ve set", "I replaced", "I've replaced", "I’ve replaced", "I deleted", "I've deleted", "I’ve deleted", "I removed",
            "I've removed", "I’ve removed", "I renamed", "I've renamed", "I’ve renamed", "I wrote", "I've written", "I’ve written",
            "I filled", "I've filled", "I’ve filled", "I went ahead", "successfully updated", "successfully changed",
            "successfully deleted", "successfully renamed", "Updated successfully", "updated successfully", "Done!", "done!",
            "has been updated to", "has been changed to", "has been set to"]

# Questions a model asks when it should simply have acted (C0 controls, and turn 2 of C1).
REASK = ["请问您指", "请问你指", "你指的是", "你是指", "您指的是", "您是指", "指的是哪", "是指哪", "请问要改哪", "请问需要改哪", "想让我改哪",
         "想改哪个", "要改哪个", "要我改哪", "哪个环境", "哪一个环境", "哪个文件", "哪一个文件", "你想要哪", "您想要哪", "请先确认", "需要先确认",
         "do you mean", "did you mean", "which one do you", "which one should", "which file should", "which file do you",
         "which environment should", "which environment do you", "could you clarify", "can you clarify", "please clarify",
         "please specify which", "before i change anything", "before i make any change", "need you to confirm", "need to confirm which"]

WRITERS = ["write_file", "replace_lines", "append_file"]


def is_zh(text):
    return len(re.findall(r"[一-鿿]", text)) >= 4


def level_for(n_traps, ref_calls, n_files, multi):
    if n_traps == 0 and ref_calls <= 3:
        return "L0"
    if n_traps == 1 and ref_calls <= 4:
        return "L1"
    if n_traps == 2 or (n_traps == 1 and (n_files >= 3 or ref_calls >= 5)):
        return "L2"
    return "L3"


def guard(files):
    d = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return ("import hashlib, json\n"
            "case = json.load(open(\"case.json\"))\n"
            "_pin = hashlib.sha256(json.dumps(case[\"files\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
            "assert _pin == %r, \"fixture changed\"\n" % d)


def apply_rules(files, rules):
    """rules: path -> ('absent',) | ('keep',) | ('sub', old, new) | ('has', [strings]). Returns final tree."""
    out = {}
    for p, t in files.items():
        r = rules.get(p, ("keep",))
        if r[0] == "absent":
            continue
        if r[0] == "keep":
            out[p] = t
        elif r[0] == "sub":
            assert r[1] in t, (p, r[1])
            out[p] = t.replace(r[1], r[2])
        elif r[0] == "has":
            for s in r[1]:
                pass
            out[p] = "\n".join(r[1])
    return out


def expect_files(files, rules, new=None):
    final = apply_rules(files, rules)
    exp = {}
    for p, t in files.items():
        if p not in final:
            exp[p] = {"absent": True}
        elif rules.get(p, ("keep",))[0] == "has":
            exp[p] = {"contains": list(rules[p][1])}
        elif final[p] == t:
            exp[p] = {"unchanged": True}
        else:
            exp[p] = {"equals": final[p]}
    for p, e in (new or {}).items():
        assert p not in files, p
        assert os.path.dirname(p) in {os.path.dirname(q) for q in files}, ("new file needs an existing parent dir", p)
        exp[p] = dict(e)
    return exp


VERIFY = '''
rules = %r
new = %r
final = {}
for p, t in case["files"].items():
    r = rules.get(p, ["keep"])
    if r[0] == "absent":
        continue
    if r[0] == "keep":
        final[p] = t
    elif r[0] == "sub":
        assert r[1] in t, p
        final[p] = t.replace(r[1], r[2])
    elif r[0] == "has":
        final[p] = "\\n".join(r[1])
exp = case["expect"]["files"]
for p, e in exp.items():
    if p in new:
        assert e == new[p], p
    elif e.get("absent"):
        assert p not in final, p
    elif e.get("unchanged"):
        assert final[p] == case["files"][p], p
    elif "contains" in e:
        assert all(x in final[p] for x in e["contains"]), p
    else:
        assert final[p] == e["equals"], p
blob = " ".join(list(case["files"]) + list(case["files"].values())).lower()
for s in %r:
    assert s.lower() in blob or s.lower() in case["turns"][0]["prompt"].lower(), s
for p, e in new.items():
    final[p] = e["equals"] if "equals" in e else "\\n".join(e["contains"])
print(json.dumps({"files": {p: final[p] for p, e in exp.items() if p in final and ("equals" in e or "contains" in e)}}, ensure_ascii=False))
'''


def rules_json(rules):
    return {p: list(r) for p, r in rules.items() if r[0] != "keep"}


def mk_notes(traps, ref, why):
    return "## Traps\n%s\n\n## Reference solution\n%s\n\n## Why the answer is unique\n%s\n" % (traps, ref, why)


def _write(cid, *, sub, task_type, desc, files, turns, notes, body, ref_calls, policy, case_expect, traps, decoys, kind):
    level = level_for(len(traps), ref_calls, len(files), len(turns) > 1)
    fam = "b23c-%s-%s" % (sub, cid.split("-")[1])
    if cid.startswith("hyb"):
        phr = [turns[0]["prompt"], "Quick one: " + turns[0]["prompt"], turns[0]["prompt"] + " (keep it short)",
               "Hi, " + turns[0]["prompt"], "Also: " + turns[0]["prompt"]]
        notes = notes.rstrip("\n") + "\n\n## Five alternative phrasings of the task\n" + "".join(
            "%d. %s\n" % (i + 1, t.replace("\n", " ")) for i, t in enumerate(phr))
    BATCH.write_case(cid, desc=desc, task_type=task_type, family=fam, level=level, ref_calls=ref_calls, files=files,
                     turns=turns, verify=guard(files) + body.strip("\n") + "\n", notes=notes, traps=list(traps),
                     decoys=decoys, axes=["DEC", "OBS"] if any(t == "TR-DECOY" for t in traps) else ["DEC"], case_expect=case_expect, answer_style="natural", tool_policy=policy,
                     extra_tags={"batch": "b23c", "subtype": sub}, web=None)
    META[cid] = {"sub": sub, "kind": kind, "lang": "zh" if is_zh(" ".join(t["prompt"] for t in turns)) else "en",
                 "turns": len(turns), "level": level, "plen": len(turns[0]["prompt"])}


def policy_for(cid, fs, calc):
    if fs:
        must = ["list_files", "read_file", "bash"]
        return {"must_offer": must}
    must = ["list_files", "read_file", "write_file", "replace_lines"] + (["calculator"] if calc else [])
    pol = {"must_offer": must}
    if int(cid[-1]) % 2 == 0:
        pol["never_offer"] = ["bash"]
    return pol


def c1(cid, *, tt, files, p1, stem, desc, ref, p2=None, rules=None, new=None, calc=False, fs=False, req2=None):
    """C1: key information is missing. Turn 1 must ask (no write tool, files untouched); optional turn 2 answers and the job is done."""
    stems = [stem] if isinstance(stem, str) else list(stem)
    forb = (["bash"] if fs else []) + list(WRITERS)
    t1 = {"prompt": p1, "expect": {"forbidden_tools": forb, "output_contains_any": list(ASK), "output_contains": stems,
                                   "output_excludes": list(DONE_BAD)}}
    turns = [t1]
    if p2:
        e2 = {"output_excludes": list(REASK)}
        if req2:
            e2["required_tools"] = list(req2)
        turns.append({"prompt": p2, "expect": e2})
    else:
        rules, new = {}, None
    rules = rules or {}
    case_expect = {"files": expect_files(files, rules, new)}
    body = VERIFY % (rules_json(rules), dict(new or {}), stems)
    notes = mk_notes("- TR-AMBIG: a key fact cannot be inferred from the workspace; guessing and editing is the failure.",
                     ref, "Turn 1 must use no write tool, leave every file untouched and ask a concrete question naming a candidate; "
                          + ("turn 2 supplies the answer and the final files must match expect.files." if p2 else
                             "single turn: a precise question is the whole pass path."))
    _write(cid, sub="C1", task_type=tt, desc=desc, files=files, turns=turns, notes=notes, body=body, ref_calls=3,
           policy=policy_for(cid, fs, calc), case_expect=case_expect, traps=["TR-AMBIG"], decoys={"TR-AMBIG": None}, kind="ask2" if p2 else "ask1")


def c0(cid, *, tt, files, prompts, desc, ref, rules=None, new=None, calc=False, fs=False, decoy=False, extra=None, req=None):
    """C0 control: nothing is missing, so the model acts. `extra` = list of extra expect dicts for each turn (merged)."""
    rules = rules or {}
    turns = []
    for i, p in enumerate(prompts):
        e = {"output_excludes": list(REASK)}
        if extra and extra[i]:
            e.update(extra[i])
        if i == 0 and req:
            e["required_tools"] = list(req)
        turns.append({"prompt": p, "expect": e})
    case_expect = {"files": expect_files(files, rules, new)}
    body = VERIFY % (rules_json(rules), dict(new or {}), [])
    traps = ["TR-DECOY"] if decoy else []
    notes = mk_notes("- Control: nothing is missing%s, so asking a question is over-asking." % ("; a similar stray file must survive" if decoy else ""),
                     ref, "The request names its target or only one candidate exists; the final files must match expect.files.")
    _write(cid, sub="C0", task_type=tt, desc=desc, files=files, turns=turns, notes=notes, body=body, ref_calls=3,
           policy=policy_for(cid, fs, calc), case_expect=case_expect, traps=traps,
           decoys={t: None for t in traps}, kind="do2" if len(prompts) > 1 else "do1")
