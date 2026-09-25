## Traps
- TR-DECOY: logs/manifest-push.log gives each undelivered batch one terminal line (`batch <id> undelivered reason=<reason>`), but the same journal is full of louder and far more numerous refusal lines: `transmission refused status=503 attempt=1`, `attempt=2`, and so on. Counting those lines instead of the terminal ones gives 12. Counting the distinct batches that ever show a refusal gives 7 (B-7311, B-7324, B-7349, B-7356, B-7361, B-7377, B-7390). The rotated journal logs/manifest-push.log.1 holds the 14 September run, whose five undelivered batches (B-7203, B-7226, B-7240, B-7268, B-7285) push a directory-wide count to 10.

## Reference solution
1. List the workspace: README.md plus logs/manifest-push.log and logs/manifest-push.log.1.
2. Read README.md. The journal is rotated at the start of the next run, so manifest-push.log is the run that started most recently and .log.1 is the run from the night before; a batch ends a run undelivered when it is parked for a payload problem or is still refused on its third attempt, and each undelivered batch gets exactly one terminal line.
3. Read logs/manifest-push.log. Its lines all carry 2026-09-15 timestamps, so it is the 15 September run. The terminal lines are B-7302, B-7324, B-7349, B-7361 and B-7377 = 5.

## Why the answer is unique
The question asks how many batches the 15 September run left undelivered, and README.md fixes what that means: an undelivered batch is one that reached a terminal state (parked on a payload problem, or still refused on its third attempt), and the run writes exactly one terminal line for it. Every such line in logs/manifest-push.log is unambiguous, and none of those batches has a second terminal line.

The decoy 12 counts every line that reports a refused transmission. That is not a batch count at all. Two of the twelve are the retries of B-7311 and one each belongs to B-7356 and B-7390, and all three of those batches were delivered on a later attempt inside the same run, so their refusals are retries rather than outcomes. The remaining refusals are repeat attempts of batches already counted once by their terminal line. A refusal line is an attempt; only the terminal line is an outcome.

The other wrong values fall to the same reading. 7 counts the batches with any refusal, but README.md says a batch that gets through on a later attempt is delivered, so B-7311, B-7356 and B-7390 are not undelivered. 10 adds the five undelivered batches of the 14 September journal, which is a different run from the one the question names. With the terminal lines counted once each, the answer is 5.

## Fixture notes
The workspace holds no code: README.md documents the retry policy and the rotation order, and the two journals are plain text with one event per line. manifest-push.log is the 15 September 2026 run and manifest-push.log.1 the 14 September 2026 run; the reason codes (attempts_exhausted, payload_rejected, payload_too_large) all follow the policy stated in README.md.
