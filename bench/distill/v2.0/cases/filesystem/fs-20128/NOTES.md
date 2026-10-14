## Traps
- No directory listing tool: find the file by searching contents, or with find/ls in the shell.

## Reference solution
Turn 1: bash find . -name deploy.sh. Turn 2: find . -name '*.sh' | wc -l -> 4.

## Why the answer is unique
Four .sh files in the tree.
