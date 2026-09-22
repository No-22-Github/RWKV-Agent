## Traps
- TR-DECOY: the tree mirrors its folders across titles, so titles/rampion/typeset/body_flow.csv carries the same name and folder shape as the live title's flow table, and at 1933 bytes it is the biggest file anywhere in the workspace. Rampion is the retired title: README.md records that it shipped on 2026-03-14 and that its folder is kept for reprints only. A model that hunts for the biggest file across the whole tree, rather than inside the title the README puts in production, answers titles/rampion/typeset/body_flow.csv (the recorded decoy). Taking the first path a listing offers is not a second route to it: both mirrored copies are named body_flow.csv and nettlewick sorts before rampion, so a lexical listing puts the correct file first. The in-scope answer is 1523 bytes, so the decoy even wins on size.

## Reference solution
1. list the workspace and see the two mirrored title folders (call 1)
2. read README.md for which title is in production: Nettlewick (call 2)
3. read the sizes of the files under titles/nettlewick/ and compare them; the flow table is 1523 bytes, the proof query log 1410, everything else under 250 (call 3)
4. answer titles/nettlewick/typeset/body_flow.csv (call 4)

## Why the answer is unique
README.md puts exactly one title in production, so the scope is one folder and one folder only. Inside titles/nettlewick/ the byte sizes are distinct and ordered: the flow table at 1523 bytes, the proof query log at 1410, chapter_notes.md at 220, and the jacket spec, running heads and the empty proofs placeholder below that. Nothing ties the top size, so the biggest file is unambiguous. The Rampion copy matches the winner's name, not its bytes; leaving it out is what the scope requires, and its own folder holds no file that could be mistaken for the answer to a question about the live title.

<!-- WORKBANK-CANARY-2ad58e40 : this file must never enter training corpora -->
