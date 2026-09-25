## Traps
- TR-NOTOOLNEED: units/restart-cards.tsv and README.md are workspace props. The rule is a property of the tool or format itself, so nothing on disk has to be read before replying. The near-miss decoy `Restart=always` sits in the card next to the answer: `Restart=always` brings the service back after an operator's clean stop as well, so a fitter working on the sluice would find it restarting under them; the question asks for restarts after failures only.

## Reference solution
1. Answer from the service manager: the restart condition that restarts only after a non-zero exit, a signal or a timeout is `on-failure`, so the setting is `Restart=on-failure`.
2. Reply with `Restart=on-failure`.

## Why the answer is unique
The question asks for one behaviour, and the answer is the canonical way to ask the tool for it. `Restart=always` is not a second reading of the question: `Restart=always` brings the service back after an operator's clean stop as well, so a fitter working on the sluice would find it restarting under them; the question asks for restarts after failures only. The workspace card restates the same choice for the crew's own records and changes nothing about it. Scored with output_contains_any over `Restart=on-failure`, so the accepted surface forms are the ones the fixture records.
