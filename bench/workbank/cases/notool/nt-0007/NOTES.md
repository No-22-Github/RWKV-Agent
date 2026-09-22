## Traps
- TR-NOTOOLNEED: the request names a concrete file in the workspace
  (tools/review_queue.py), so it invites a look at that script or a search of
  the tree, but the command that attributes each line of a file to its last
  commit is fixed Git knowledge and needs no call. The workspace script is
  the decoy: it is the same file the request names, yet it is an unrelated
  triage helper, so reading it yields no command. The careless wrong ANSWER,
  when the model describes history rather than line attribution, is a
  history-dump command such as `git log -p tools/review_queue.py`, recorded in
  trap_decoys.

## Reference solution
No steps; ref_calls is 0. Reply with the command `git blame
tools/review_queue.py` directly, so that the reply contains the string
`git blame`. The correct pass criterion is the answer alone: under scorer v3
the turn's `tools: []` no longer fails a turn, it only feeds the
no_call_accuracy / active_no_call call-discipline metrics. An answer built
from the decoy script (or one that only shows history) does not contain
`git blame` and fails output_contains.

## Why the answer is unique
`git blame` is the single Git subcommand defined for annotating each line of
a file with the commit and author that last changed it; nothing in the
workspace redefines it. The registered decoy `git log -p tools/review_queue.py`
is wrong for a concrete reason: `git log` lists commits (optionally with
patches) and never maps individual lines to the commit that introduced them,
which is exactly what the request asks for. The decoy file is a Python
triage helper whose body contains no Git invocation at all, so no reading of
it can produce a competing command.

## Grading note
v1 required the literal substring "git blame", which failed `git annotate` -
the same command under its other porcelain name, with the same per-line
commit and author output. v2 accepts either spelling in both capitalisations.
The case is about naming the command that answers the question without a tool
to run it, not about which of its two names the model learned.

<!-- WORKBANK-CANARY-9a24e5b7 : this file must never enter training corpora -->
