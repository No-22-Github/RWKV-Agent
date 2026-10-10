## Traps
- TR-NOTOOLNEED: deploys/rollback-cards.tsv and README.md are workspace props. The rule is a property of the tool or format itself, so nothing on disk has to be read before replying. The near-miss decoy `kubectl rollout restart` sits in the card next to the answer: `kubectl rollout restart` starts the current revision again, so the bad revision keeps serving; it changes nothing about which revision the deployment runs.

## Reference solution
1. Answer from the cluster tool: rolling back to the revision before the current one is `kubectl rollout undo`.
2. Reply with `kubectl rollout undo`, or one of the accepted spellings `rollout undo`.

## Why the answer is unique
The question asks for one behaviour, and the answer is the canonical way to ask the tool for it. `kubectl rollout restart` is not a second reading of the question: `kubectl rollout restart` starts the current revision again, so the bad revision keeps serving; it changes nothing about which revision the deployment runs. The workspace card restates the same choice for the crew's own records and changes nothing about it. Scored with output_contains_any over `kubectl rollout undo` or `rollout undo`, so the accepted surface forms are the ones the fixture records.
