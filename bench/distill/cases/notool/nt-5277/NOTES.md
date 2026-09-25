## Traps
- TR-NOTOOLNEED: deploys/instance-logs.tsv and README.md are workspace props. The rule is a property of the tool or format itself, so nothing on disk has to be read before replying. The near-miss decoy `kubectl logs --follow` sits in the card next to the answer: `kubectl logs --follow` streams the log of the running instance, which is the one that started after the jam, so the lines from the dead instance never appear.

## Reference solution
1. Answer from the cluster tool: the flag that reads the log of the container instance that terminated is `--previous`, so the command is `kubectl logs --previous`.
2. Reply with `kubectl logs --previous`, or one of the accepted spellings `logs --previous`, `--previous`.

## Why the answer is unique
The question asks for one behaviour, and the answer is the canonical way to ask the tool for it. `kubectl logs --follow` is not a second reading of the question: `kubectl logs --follow` streams the log of the running instance, which is the one that started after the jam, so the lines from the dead instance never appear. The workspace card restates the same choice for the crew's own records and changes nothing about it. Scored with output_contains_any over `kubectl logs --previous` or `logs --previous` or `--previous`, so the accepted surface forms are the ones the fixture records.
