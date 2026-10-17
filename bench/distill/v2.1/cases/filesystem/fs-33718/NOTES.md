## Traps
Hidden files plus files inside a hidden directory (.config) whose own names are not dotted.

## Reference solution
find -name '.*'.

## Why the answer is unique
.bashrc .profile .draft.tmp = 3; hidden dirs .config (3 files) and .ssh (1) = 4.
