## Traps
- TR-READONLY: 构建/vendor/*.pyc ship with a third-party wheel and have no source (构建/README.md).
- TR-DECOY: 构建/pkg/说明.pyc.md is a document whose name contains .pyc but ends in .md.

## Reference solution
1. bash: `find 构建 -name '*.pyc' | grep -v /vendor/ | xargs rm`
2. bash: `find 构建 -type f` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the four .pyc files outside vendor are gone; sources, vendor .pyc files and the pyc doc remain).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. 构建 里所有 .pyc 文件删除，.py 源码和 vendor 里第三方自带的保留，检查后回复 DONE。
2. 请清掉 构建 目录树中的编译产物 .pyc（不含 vendor），源文件别动，删完确认并回复 DONE。
3. 构建 下面的 pyc 缓存全部清理掉，README 里写了不能删的保持原样，核对后回复 DONE。
4. 删除 构建 里的 *.pyc，但构建/vendor 和说明文档不要删，完成后检查并回复 DONE。
5. 把 构建 目录里能重新生成的 .pyc 文件都删了，其余文件保持不变，确认后回复 DONE。
