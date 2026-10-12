## Traps
- TR-READONLY: docs/legacy is matched by exact upper-case names by an FTP job (docs/README.md).
- TR-DECOY: INTRO.TXT.sig is a detached signature whose name contains .TXT but ends in .sig.

## Reference solution
1. bash: `for f in $(find docs -name '*.TXT' | grep -v /legacy/); do mv "$f" "${f%.TXT}.txt"; done`
2. bash: `find docs -type f` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the four documents now end in .txt; the legacy files and INTRO.TXT.sig keep their names).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. Rename all .TXT files in docs to lowercase .txt, except the ones the README protects. Verify, then reply DONE.
2. docs 下面（含子目录）的 .TXT 文件统一改成 .txt 后缀，legacy 目录和签名文件不动，检查后回复 DONE。
3. Make the extensions of the documents in docs lowercase (.TXT becomes .txt), skipping docs/legacy and *.sig files. Check and reply DONE.
4. Please rename docs/**/*.TXT to .txt using docs/README.md for the exceptions, confirm the result and reply DONE.
5. 把 docs 里的大写扩展名 .TXT 批量换成小写 .txt，README 里禁止改名的保持原样，改完确认并回复 DONE。
