## Traps
- TR-DECOY: the Discussion section has a vague "someone should look into" parking line; it is not an action item. Not-an-action-item lines in todo.md would appear as extra lines.
- The Marcus line is marked (done) and sits in the middle, so keeping it breaks the contiguous three-line block that is checked.
Turn 1 is not judged separately.

## Reference solution
1. Read the notes, write todo.md with four lines.
2. Rewrite with deadlines in parentheses, dropping Marcus's done item.

Final todo.md:
```
- Dana: reorder the label scanner (19 Sep)
- Priya: update the onboarding checklist (24 Sep)
- Leo: book the October offsite venue (30 Sep)
```

## Why the answer is unique
Turn 1 fixes the line template and the order; turn 2 fixes the deadline placement. The checked block is the three remaining lines, contiguous. Limitation: contains cannot reject extra lines before/after the block (e.g. a parking line), so those are only caught if inserted inside it.

EXAM-CANARY-df5139d5
