## Traps
- TR-NOTOOLNEED: ops/tunnel-cards.tsv, README.md and notes/field-notes.txt are props. Which side of a session a forward listens on is a property of the session tool, so nothing has to be read. The near-miss decoy `-L 9142:localhost:9142` opens the listening port on the machine that starts the session, which is the controller itself, so the workstation still cannot reach the tool.

## Reference solution
1. Answer from the tool: a forward whose listening end is the far machine is requested with `-R`, and the workstation reaches the tool by asking for `localhost:9142` on the controller, so the value is `9142:localhost:9142`.
2. Reply with `-R 9142:localhost:9142`.

## Why the answer is unique
The question puts the tool on the controller and the engineer on the workstation, and `-R` is the flag that opens the listening end on the remote machine of the session, so the workstation's own localhost reaches the controller's tool. `-L` cannot be a reading of the question: it opens the listening end on the machine that starts the session, the controller, where nobody needs to reach the tool, and the workstation side stays closed.
