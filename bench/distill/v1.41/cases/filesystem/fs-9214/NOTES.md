## Traps
- TR-READONLY: 素材/模板包 is a signed bundle whose .DS_Store is covered by the signature (素材/README.md).
- TR-DECOY: 说明.DS_Store.txt is a documentation file whose name contains .DS_Store.

## Reference solution
1. bash: `find 素材 -name .DS_Store | grep -v /模板包/ | xargs rm`
2. bash: `find 素材 -name '*DS_Store*'` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the four .DS_Store files outside the template bundle are gone; media, the bundle's .DS_Store and the doc remain).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. 删除 素材 下所有的 .DS_Store（模板包里的除外），素材文件本身不要动，检查后回复 DONE。
2. 请把 素材 目录树里 macOS 留下的 .DS_Store 清理掉，签名包保持原样，核对后回复 DONE。
3. 同步前清理：素材/** 的 .DS_Store 全部删除，README 里说明的例外保留，完成后检查并回复 DONE。
4. 找出 素材 里的 .DS_Store 文件并删除，模板包目录和普通文档别动，确认后回复 DONE。
5. 素材 里的 Finder 元数据文件 .DS_Store 统统删掉，只有素材/README.md 点名的保留，检查后回复 DONE。
