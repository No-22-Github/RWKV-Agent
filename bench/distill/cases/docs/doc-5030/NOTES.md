## Traps
- TR-NEARNAME: the register lists `protocols/equine-colic.md`, while the folder holds `protocols/equine-colic-notes.md`. A solver that matches on the opening words reads the near name as the entry and reports `protocols/equine-colic-notes.md`; the register names no such path.

## Reference solution
1. List the workspace: a cover note, the register and the protocols held in the folder.
2. Read `registers/protocol-set.txt`: protocols/equine-colic.md, protocols/canine-vaccination.md, protocols/feline-anaesthesia.md, protocols/rabbit-dentistry.md.
3. Check each entry against the folder. Three of the four have a file at exactly the path the register writes; `protocols/equine-colic.md` has none, because the colic document in the folder is `protocols/equine-colic-notes.md`.

## Why the answer is unique
Three register entries resolve to a file at exactly the path they name, and the fourth does not. The decoy `protocols/equine-colic-notes.md` is a document of the folder rather than an entry of the register, and its name carries a word the entry does not, so it is a different path from the one being checked; the other protocols in the folder each match an entry word for word, so there is no second near name to weigh against this one. The answer is protocols/equine-colic.md.
