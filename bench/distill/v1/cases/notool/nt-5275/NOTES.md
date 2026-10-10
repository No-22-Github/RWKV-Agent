## Traps
- TR-NOTOOLNEED: manifests/check-fields.tsv and README.md are workspace props. The rule is a property of the tool or format itself, so nothing on disk has to be read before replying. The near-miss decoy `livenessProbe` sits in the card next to the answer: `livenessProbe` restarts the container when the check fails, so a container that is merely still loading its data would be killed and started again; the question asks for it to be held off traffic instead.

## Reference solution
1. Answer from the container platform: the field whose check decides whether a container may receive traffic is `readinessProbe`.
2. Reply with `readinessProbe`.

## Why the answer is unique
The question asks for one behaviour, and the answer is the canonical way to ask the tool for it. `livenessProbe` is not a second reading of the question: `livenessProbe` restarts the container when the check fails, so a container that is merely still loading its data would be killed and started again; the question asks for it to be held off traffic instead. The workspace card restates the same choice for the crew's own records and changes nothing about it. Scored with output_contains_any over `readinessProbe`, so the accepted surface forms are the ones the fixture records.
