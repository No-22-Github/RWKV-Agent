## Traps
- TR-READONLY: 手册/归档 holds withdrawn old versions and stays as it is (手册/README.md).
- TR-DECOY: 考勤.txt.bak is an editor backup, not a handbook page; it ends in .bak, not .txt.

## Reference solution
1. bash: `find 手册 -name '*.txt' | grep -v /归档/ | xargs sed -i '1i 内部资料，禁止外传'`
2. bash: `head -n 1 手册/*.txt 手册/分公司/*.txt` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the five handbook pages (including 北京.txt) start with the header; the archive and the .bak are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. 手册目录（含子目录）里的 .txt 文件，开头统一插入一行「内部资料，禁止外传」，作废的归档版本除外，检查后回复 DONE。
2. 在 手册 下每份 .txt 的第一行加上保密抬头「内部资料，禁止外传」，README 里说不改的别改，完成后回复 DONE。
3. 请为 手册 里的正式文本文件添加首行「内部资料，禁止外传」，备份文件和归档不要碰，改完核对并回复 DONE。
4. 每个 手册/**/*.txt（归档目录除外）都在最前面插一行「内部资料，禁止外传」，然后确认并回复 DONE。
5. 给手册加保密抬头：把「内部资料，禁止外传」放在每个 .txt 的第一行，遵守 手册/README.md 的例外，检查完回复 DONE。
