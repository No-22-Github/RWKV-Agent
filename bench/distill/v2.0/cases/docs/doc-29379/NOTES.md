## Traps
- TR-DECOY: 3.2.0 mentions --legacy as deprecated; CHANGELOG-v2.md shows 2.9.0 adding it.

## Reference solution
1. read_file CHANGELOG.md
Final answer: --legacy was removed in 3.4.0 (3.2.0 only deprecated it).

## Why the answer is unique
The user names CHANGELOG.md; only its live line holds the answer. 3.2.0 only deprecated the flag and 2.9.0 (other file) added it.
Why bash is not the tool here: one named file and one fact, read_file is the direct read. Bash is offered, but a shell call would be wasted effort.

## Five alternative phrasings of the task
1. In CHANGELOG.md, in which release was --legacy actually removed (not just deprecated)?
2. CHANGELOG.md: what version dropped the --legacy flag?
3. Which release of this project took out --legacy? See CHANGELOG.md.
4. Check CHANGELOG.md and tell me the version where --legacy was removed.
5. When did --legacy go away, per CHANGELOG.md? Give the version.
