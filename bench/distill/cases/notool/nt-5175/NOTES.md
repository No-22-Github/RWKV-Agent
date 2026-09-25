## Traps
- TR-NOTOOLNEED: ops/create-mode-cards.tsv and README.md are props. The creation mask is a property of the process, so no file has to be read. The near-miss decoy `umask 022` clears only the group and other write bits, so every file the job creates stays readable by accounts outside the group, which the question rules out.

## Reference solution
1. Answer from the mask's bits: the job needs the owner untouched, group read and directory traverse left in place, and group write plus all outside bits cleared, which is `umask 027`.
2. Reply with `umask 027` (`umask 0027` is the same mask written in the four-digit form).

## Why the answer is unique
The question fixes the owner's access, the group's read and traverse access and the absence of any outside access, and `027` is the mask whose bits are exactly those requests: it clears group write and every outside bit while leaving group read and traverse. `umask 022` cannot be a reading of the question, because it clears only the write bits, so created files remain readable by anyone, which is the access the question forbids. Writing the mask with a leading zero is the same mask.
