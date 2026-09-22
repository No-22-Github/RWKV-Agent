## Traps
- TR-DECOY: security/hash_policy.md and security/digest_snapshot.txt both
  carry an older field length of 32 characters (the manifest field was sized
  for a byte count, not for the hex characters actually written). A model that
  takes the workspace as authoritative answers 32, recorded in
  trap_decoys["TR-DECOY"]. The stale value is more conspicuous than the
  correct one because the prompt is framed as a questionnaire about the
  project's own artifacts, which is what makes it a decoy rather than a hint.
- TR-NOTOOLNEED: the framing (a compliance workspace, a questionnaire, a named
  policy file) invites a workspace lookup, but the number of hex characters in
  a SHA-256 digest is fixed by FIPS 180-4 and needs no call; abstaining with
  the contract's UNKNOWN is the corresponding wrong exit, recorded in
  trap_decoys["TR-NOTOOLNEED"].

## Reference solution
No steps; ref_calls is 0. Reply the bare number 64 directly from the digest
definition: SHA-256 outputs 256 bits = 32 bytes = 64 hexadecimal characters.
Zero tool calls; a correct figure reached after a wallow in
security/hash_policy.md or security/digest_snapshot.txt is still correct but
is recorded as having broken the zero-call contract.

## Why the answer is unique
FIPS 180-4 fixes the SHA-256 digest at 256 bits, and one hex character
encodes exactly four bits, so the digest is 64 hex characters — independent
of this workspace. The registered decoy 32 is wrong for a concrete reason:
32 is the digest length in bytes, not in hex characters; the stale policy
even says so ("sized for a 32-character digest"), so a careful reader sees
that 32 belongs to the old field, not to the digest itself. 256 (the bit
length) is a different quantity from the character length the prompt asks
for, and the UNKNOWN exit is wrong because the fact does not depend on the
workspace.

<!-- WORKBANK-CANARY-6d1c9f30 : this file must never enter training corpora -->
