## Traps
- TR-READONLY: repo/third_party keeps upstream's own .orig/.rej files (repo/README.md).
- TR-DECOY: repo/src/ORIGIN.md has a name that starts like .orig but is documentation.

## Reference solution
1. bash: `find repo -name '*.orig' -o -name '*.rej' | grep -v /third_party/ | xargs rm`
2. bash: `find repo -type f` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the four patch leftovers in src are gone; third_party files, sources and ORIGIN.md remain).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. Delete all *.orig and *.rej files in repo except the ones under third_party; keep the source files. Verify and reply DONE.
2. repo 里失败补丁留下的 .orig 和 .rej 文件全部删除，第三方目录里的保留，检查后回复 DONE。
3. Remove patch leftovers (*.orig, *.rej) from the repo tree, skipping repo/third_party, then confirm and reply DONE.
4. Please purge .orig/.rej files under repo except where the README says to keep them, check what is left, and reply DONE.
5. 清理 repo 目录：*.orig、*.rej 删掉，third_party 和正常源码、文档保持不变，核对后回复 DONE。
