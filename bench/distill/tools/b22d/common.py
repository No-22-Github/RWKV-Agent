"""b22d (v2.2: calculator boundary, ids 34301-34370) shared framework.

A case = prompts + compute() -> one number per turn + the numbers the prompts
must literally contain (GIVEN). compute is embedded in verify.py and re-run
there; expected_number in case.json is generated from the same function.
"""
import hashlib
import inspect
import json
import os
import re
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch, Sidecar, check_reference  # noqa: E402,F401

BATCH = Batch(salt="b22d", author="llm:claude-sonnet-b22d", version="v2.2", tool_catalog="agent-tool-v3.1")
META = {}
_VOCAB = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "workbank", "tag-vocab.json")))
TRAP_AXIS = {k: v.get("axis") for k, v in _VOCAB["traps"].items()}
TRAP_WORDS = {k: v.get("forbidden_words") or [] for k, v in _VOCAB["traps"].items()}
TOOLNAMES = _VOCAB["tools"] + ["bash", "awk"]
SIDE = []


def sidecar():
    if not SIDE:
        SIDE.append(Sidecar())
    return SIDE[0]


def is_zh(text):
    return len(re.findall(r"[一-鿿]", text)) >= 4


NAMES = ["晨光文具", "Harbor Labs", "青禾农场", "Delta Print", "云岭茶社", "Kestrel Works", "海盐面包房", "Orchard Notes",
         "南湾物业", "Pine Studio", "星火教育", "Lumen Desk"]


def ws(i):
    """Small unrelated workspace (same shape for every subtype)."""
    n = NAMES[i % len(NAMES)]
    return {"README.md": "# %s workspace\n\nNotes and small tables live here (item %d).\n" % (n, i),
            "misc/todo-%d.txt" % (i * 7 % 97 + 3): "- check shelf %d\n- reorder item %d\n" % (i % 13 + 1, i * 3 % 50 + 10)}


def T(p, tol=0.01):
    return {"p": p, "tol": tol}


def mk(cid, *, sub, turns, compute, given, decoy, notes, alts=None, must=None, never=None, files=None,
       forbid=None, req=None, max_calls=None, task=None, rc=0, ref=None):
    """turns: list of T(); compute() -> list of numbers (len == turns);
    given: strings that must literally occur in the prompts;
    ref: (commands, text-that-stdout-must-contain) replayed in the sandbox."""
    nums = compute()
    assert len(nums) == len(turns), cid
    src = re.sub(r"def \w+\(", "def compute(", textwrap.dedent(inspect.getsource(compute)), count=1)
    ns = {}
    exec(src, ns)
    assert ns["compute"]() == nums, cid
    allp = "\n".join(t["p"] for t in turns)
    for g in given:
        assert g in allp, (cid, g)
    low = re.sub(r"\s+", " ", allp.lower())
    for tn in TOOLNAMES:
        assert tn not in low, (cid, tn)
    assert not re.search(r"测试|判据|verify|benchmark|心算|计算器|calculator", low), cid
    if ref:
        cmds, want = ref
        err = check_reference(sidecar(), files or {}, cmds, lambda out, root: None if want in out else
                              "stdout %r lacks %r" % (out, want))
        assert err is None, (cid, err)
    scenario_nt = cid.startswith("nt-")
    if sub == "D1":
        traps = ["TR-NOTOOLNEED"]
        task = task or ("unit_convert" if scenario_nt else "special_tool")
    else:
        traps = ["TR-DEFN"]
        task = task or "special_tool"
    tturns = []
    for t, v in zip(turns, nums):
        e = {"expected_number": float(v), "expected_number_in_text": True, "tolerance": t["tol"]}
        if sub == "D1":
            e["tools"] = []
        d = {"prompt": t["p"], "expect": e}
        tturns.append(d)
    files = files if files is not None else {}
    cexp = {}
    for path in files:
        cexp.setdefault("files", {})[path] = {"unchanged": True}
    if max_calls:
        cexp["max_calls"] = dict(max_calls)
    if forbid:
        for d in tturns:
            d["expect"]["forbidden_tools"] = list(forbid)
    if req:
        for d in tturns:
            d["expect"]["required_tools"] = list(req)
    digest = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    verify = ("import hashlib, json\n"
              "case = json.load(open(\"case.json\"))\n"
              "_pin = hashlib.sha256(json.dumps(case[\"files\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
              "assert _pin == %r, \"fixture changed\"\n" % digest + src + "\n"
              "GIVEN = %s\n" % json.dumps(list(given), ensure_ascii=False) +
              "PROMPTS = \"\\n\".join(t[\"prompt\"] for t in case[\"turns\"])\n"
              "assert all(g in PROMPTS for g in GIVEN)\n"
              "ANS = compute()\n"
              "assert len(ANS) == len(case[\"turns\"])\n"
              "for turn, v in zip(case[\"turns\"], ANS):\n"
              "    assert abs(turn[\"expect\"][\"expected_number\"] - v) < 1e-9\n"
              "print(json.dumps({\"expected_number\": float(ANS[0])}))\n")
    pol = {}
    if must:
        pol["must_offer"] = list(must)
    if never:
        pol["never_offer"] = list(never)
    dec = {t: decoy for t in traps}
    axes = list(dict.fromkeys(["DEC" if sub == "D1" else "OBS"] + [TRAP_AXIS[t] for t in traps]))
    alt_txt = ""
    if not scenario_nt:
        assert alts and len(alts) == 5, (cid, "need 5 phrasings")
        alt_txt = "\n\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, a) for i, a in enumerate(alts))
    nt = ("## Traps\n%s\n\n## Reference solution\n%s\n\n## Why the answer is unique\n"
          "Recomputed by verify.py from the numbers in the prompt. Expected: %s%s" % (
              ", ".join(traps), notes, " ".join(repr(float(v)) for v in nums) + " (" + ", ".join(str(v) for v in nums) + "; " +
              ", ".join("%g / %.9g" % (v, v) for v in nums) + ")",
              alt_txt))
    multi = len(turns) > 1
    fam = "b22d-%s-%s" % (sub, cid.split("-")[1])
    BATCH.write_case(cid, desc="%s: %s" % (sub, notes.split(".")[0][:90]), task_type=task, family=fam, level="L1",
                     ref_calls=rc, files=files, turns=tturns, verify=verify, notes=nt, traps=traps, decoys=dec,
                     axes=axes, case_expect=cexp or None, answer_style="natural",
                     tool_policy=pol or None, extra_tags={"batch": "b22d", "subtype": sub})
    META[cid] = {"sub": sub, "zh": is_zh(allp), "multi": multi, "plen": sum(len(t["p"]) for t in turns) // len(turns),
                 "policy": "+".join(must or []) or "-"}


def P(i):
    """D1/D0 policy alternation: half the cases pin calculator into the catalog."""
    return ["calculator"] if i % 2 else None


def W(i):
    """Every third case carries the small unrelated workspace."""
    return ws(i) if i % 3 == 0 else {}
