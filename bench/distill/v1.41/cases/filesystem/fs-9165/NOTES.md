## Traps
- TR-READONLY: src/vendor/six.py is third-party code kept byte-for-byte (src/README.txt).
- TR-DECOY: src/snippets/demo.py.txt is a documentation sample whose name contains .py but is not a module.

## Reference solution
1. bash: `find src -name '*.py' | grep -v /vendor/ | xargs sed -i 's/[[:space:]]*$//'`
2. bash: `grep -rlE '[[:space:]]$' src` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the four modules have no trailing whitespace; vendor/six.py and demo.py.txt are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. Remove trailing spaces and tabs from all Python modules in src, but leave the vendored copy and the doc samples as they are. Verify, then reply DONE.
2. Trim line-end whitespace in src/**/*.py (not src/vendor), check afterwards that none is left in the files you touched, and reply DONE.
3. Clean up trailing whitespace across the .py files in src; src/README.txt names the exceptions. Confirm and say DONE.
4. Please strip trailing blanks from each .py under src except the third-party folder, double-check, and reply DONE.
5. src 里所有 .py 文件行尾的空格和制表符去掉，README.txt 里说保持原样的别动，检查后回复 DONE。
