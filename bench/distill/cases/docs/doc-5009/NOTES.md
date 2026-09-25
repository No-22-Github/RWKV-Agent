## Traps
- TR-MULTISRC: the named documents are split between lists/depot-set.txt and lists/trunk-set.txt. Working from the depot list alone finds 2 absent documents (forms/depot-handover.md, forms/consignment-note.md) and the trunk list alone also finds 2 (rates/haulage-2026.csv, notices/trunk-diversions.md), so either single list gives the decoy 2.
- TR-DUPROW: forms/consignment-note.md appears in both lists, so counting lines rather than documents gives 5 while the set is short of 4 distinct documents.

## Reference solution
1. List the workspace: a cover note, two list files and two guides.
2. Read lists/depot-set.txt: forms/depot-handover.md, guides/routing.md, forms/consignment-note.md, guides/customs.md.
3. Read lists/trunk-set.txt and fold it in: guides/routing.md, rates/haulage-2026.csv, forms/consignment-note.md, notices/trunk-diversions.md. Compared with the files present in the set, the absent documents are forms/depot-handover.md, forms/consignment-note.md, rates/haulage-2026.csv and notices/trunk-diversions.md, which is 4.

## Why the answer is unique
The decoy 2 is wrong because neither list is the whole set of named documents: the depot list and the trunk list each name two absent documents, and the union of the two names four. The decoy 5 is wrong because forms/consignment-note.md is named by both lists yet is still one missing document, and the question asks how many documents are absent, not how many lines name one. guides/routing.md and guides/customs.md are named and present, so they do not count. The answer is 4.
