## Traps
- No directory listing tool: find the file by searching contents, or with find/ls in the shell.

## Reference solution
bash: find backup -name '*.tar' | wc -l -> 7

## Why the answer is unique
.tar.sig files are decoys and do not end in .tar.
