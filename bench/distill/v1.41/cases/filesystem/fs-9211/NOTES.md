## Traps
- TR-READONLY: src/vendor is third-party code kept byte-for-byte (src/README.txt).
- TR-DECOY: src/Makefile needs real tabs and is not a .c or .h file.

## Reference solution
1. bash: `find src -name '*.[ch]' | grep -v /vendor/ | xargs sed -i 's/\t/    /g'`
2. bash: `grep -rlP '\t' src` to confirm the target files changed and the protected ones did not.
Final answer: DONE (main.c, util.c, util.h and sock.c have no tabs left; Makefile and vendor/zlib.c still contain theirs).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. Convert tab indentation to 4 spaces in the C sources and headers in src, but not the Makefile or vendor code. Verify, then reply DONE.
2. In src/**/*.c and *.h, swap each tab for four spaces; honour the exceptions in src/README.txt; check and reply DONE.
3. src 里 .c 和 .h 文件的制表符全部换成 4 个空格，Makefile 和 vendor 不动，改完检查并回复 DONE。
4. Please untabify the C code under src (4 spaces per tab) except the vendored folder and Makefile, confirm, and reply DONE.
5. Turn leading and inline tabs in src's C files into four spaces, leave what the README protects alone, check the result and reply DONE.
