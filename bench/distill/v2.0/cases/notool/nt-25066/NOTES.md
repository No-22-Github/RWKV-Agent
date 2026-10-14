## Traps
- TR-NOTOOLNEED: the field table and README are props; the policy name comes from the runtime's own vocabulary. The near-miss decoy is `restart: always`: it also survives restarts, but it revives the container after an operator stop, which the question rules out.

## Reference solution
1. Answer from the runtime's policy names: one policy restarts unconditionally, one only restarts containers that did not exit cleanly by request.
2. Reply with `restart: unless-stopped`.

## Why the answer is unique
The question names two requirements at once, and only one policy satisfies both: it must restart the container after the runtime comes back, and it must treat a stop requested by an operator as final. `always` fails the second requirement by design, and the other policies never bring the container back up after a runtime restart, so `unless-stopped` is the only value the question admits; writing the bare value states the same answer without the field name.
