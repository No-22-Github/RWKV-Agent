"""Case assembly for b21f: files + specs + prompts + per-turn bash references."""
from common import case, policy, turn, write_files
from lib import run_answers, verify_body


def make(cid, n, *, sub, fmt, evs, specs, prompts, refs, traps, decoys, nocalc, desc, notes_ref, notes_traps,
         extra_files=None, task_type="count_events", axes=("OBS",), answer_text=""):
    """evs: {path: [Ev]}; specs/prompts/refs: one per turn."""
    files = write_files(evs, fmt)
    if extra_files:
        files.update(extra_files)
    fmts = fmt
    for j, sp in enumerate(specs):   # seconds only where the conversation asks for them
        if not any("几秒" in p for p in prompts[: j + 1]):
            sp["hm"] = True
    toks = run_answers(files, fmts, specs)
    turns = [turn(p, t) for p, t in zip(prompts, toks)]
    notes = ("## Traps\n%s\n\n## Reference solution\n%s\n\nExpected tokens per turn: %s\n\n"
             "## Why the answer is unique\nThe answer is recomputed from the fixture by verify.py with an independent line parser; "
             "the bash reference is replayed in the just-bash sidecar at build time and prints the same values.\n"
             % (notes_traps, notes_ref, "; ".join(" ".join(t) for t in toks)))
    case(cid, sub=sub, desc=desc, task_type=task_type, family="b21f-%s-%02d" % (sub, n), ref_calls=3 + len(turns) - 1,
         files=files, turns=turns, verify_body=verify_body(fmts, specs), notes=notes, traps=traps, decoys=decoys,
         axes=axes, policy=policy(n, nocalc), refs=refs)
    return toks
