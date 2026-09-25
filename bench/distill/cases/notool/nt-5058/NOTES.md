## Traps
- TR-NOTOOLNEED: the workspace carries the wrapper's README and a handover note, neither of which the answer depends on. The near-miss decoy is `2>&1 > crusher.log`: it points the second stream at the terminal's current stdout and only then truncates the file, so the error text is lost and the log is replaced rather than appended.

## Reference solution
1. Answer from the shell: appending a single stream is `>>`, and folding the error stream into it is `2>&1`.
2. Reply with `>> crusher.log 2>&1` (the bash shorthand `&>> crusher.log` is the same redirection).

## Why the answer is unique
The question fixes both requirements in one snippet: the file must keep earlier content, which is what `>>` does and `>` does not, and both streams must land in it, which requires the error stream to be duplicated onto the standard output that has already been pointed at the file. `2>&1 > crusher.log` reverses that order, so the duplicate still refers to the terminal and crusher.log receives only the ordinary output; the question's "both streams" and "keep growing" together leave `>> crusher.log 2>&1` as the only short form, with `&>> crusher.log` its bash equivalent.
