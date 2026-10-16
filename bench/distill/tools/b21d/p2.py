"""31331-31370: ambiguous requests (ask first) and single-candidate controls (just do it)."""
from common import ASK, DONE_BAD, WRITERS, NOT_BASH, FILES_VERIFY, expect_files, rules_json, mk_notes, write

BUILDERS = []


def reg(f):
    BUILDERS.append(f)
    return f


def lines(rows):
    return "".join(r + "\n" for r in rows)


STR_VERIFY = '''
%s
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
'''


def clarify(cid, *, scen, task_type, files, p1, stems, must, desc, ref, p2=None, rules=None, calc=None, ans2=None, excl2=(), never=None,
            excl1=(), sub="clarify", edit=True):
    """Ask-first case. edit=True -> turn 2 is judged by final files (rules); else by ans2 (calc computes it from case files)."""
    forb = list(WRITERS) if edit else list(NOT_BASH)
    t1 = {"prompt": p1, "expect": {"forbidden_tools": forb, "output_contains_any": list(ASK), "output_contains": list(stems),
                                   "output_excludes": (list(DONE_BAD) if edit else []) + list(excl1)}}
    turns = [t1]
    case_expect = None
    if edit:
        if rules is None:
            rules = {}
        case_expect = {"files": expect_files(files, rules)}
        body = FILES_VERIFY % (rules_json(rules),)
        body += "\nassert all(any(s in p or s in t for p, t in case['files'].items()) for s in case['turns'][0]['expect']['output_contains'])\n"
    else:
        body = STR_VERIFY % (calc if (calc and p2) else "ans = case['turns'][0]['expect']['output_contains'][0]")
    if p2:
        e2 = {}
        if not edit:
            e2 = {"output_contains": [ans2]}
            assert len(ans2) >= 2
            if ans2.isascii():
                e2["output_contains_token"] = True
            if excl2:
                e2["output_excludes"] = list(excl2)
            body += "assert %r in case['turns'][1]['expect']['output_contains']\nassert str(ans) == %r\n" % (ans2, ans2)
        turns.append({"prompt": p2, "expect": e2})
    policy = {"must_offer": list(must)}
    if never:
        policy["never_offer"] = list(never)
    notes = mk_notes("- TR-AMBIG: key information is missing and several workspace items fit; guessing one is the failure.",
                     ref, "Turn 1 must use no writing tool and must ask (a question word from the list) while naming the candidates; "
                          + ("the follow-up fixes the target and the final files must equal expect.files." if edit and p2 else
                             ("the follow-up fixes the target and the answer is recomputed from the fixture." if p2 else "single turn: asking is the whole pass path.")))
    write(cid, sub=sub, task_type=task_type, desc=desc, files=files, turns=turns, notes=notes, body=body, ref_calls=3, policy=policy,
          case_expect=case_expect, traps=["TR-AMBIG"],
          decoys={"TR-AMBIG": None if edit else "picks one candidate and answers without asking"}, axes=("DEC",), kind="clarify")


def solo(cid, *, task_type, files, p1, must, desc, ref, rules=None, calc=None, ans=None, req=(), never=None, p2=None, out2=None,
         traps=(), decoys=None, sub="solo"):
    """Control: exactly one candidate, so the model acts without asking."""
    e1 = {"required_tools": list(req)} if req else {}
    case_expect = None
    if rules is not None:
        case_expect = {"files": expect_files(files, rules)}
        body = FILES_VERIFY % (rules_json(rules),)
    else:
        assert len(ans) >= 2
        e1["output_contains"] = [ans]
        if ans.isascii():
            e1["output_contains_token"] = True
        body = STR_VERIFY % calc + "assert str(ans) in case['turns'][0]['expect']['output_contains']\n"
        body = body.replace("assert all(any(s in p or s in t for p, t in case[\"files\"].items()) for s in case[\"turns\"][0][\"expect\"].get(\"output_contains\", []))\n", "")
    turns = [{"prompt": p1, "expect": e1}]
    if p2:
        e2 = {"output_contains": list(out2)}
        if all(o.isdigit() for o in out2):
            e2["output_contains_token"] = True
        turns.append({"prompt": p2, "expect": e2})
    policy = {"must_offer": list(must)}
    if never:
        policy["never_offer"] = list(never)
    notes = mk_notes("- Control: exactly one candidate exists, so asking for clarification is over-asking.%s" % (" TR-DECOY: a stray similar file must survive." if traps else ""),
                     ref, "Only one file fits the request, so the model must do the job (final files or the recomputed value).")
    write(cid, sub=sub, task_type=task_type, desc=desc, files=files, turns=turns, notes=notes, body=body, ref_calls=3 if not traps else 3,
          policy=policy, case_expect=case_expect, traps=list(traps),
          decoys=(decoys if decoys is not None else {t: (None if rules is not None else "the value of the stray file") for t in traps}),
          axes=("DEC", "OBS") if traps else ("DEC",), kind="solo")
