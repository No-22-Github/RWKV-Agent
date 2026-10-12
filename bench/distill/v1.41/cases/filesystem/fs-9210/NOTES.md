## Traps
- TR-READONLY: 文稿库/win/*.bat must stay CRLF (文稿库/README.md).
- TR-DECOY: already.txt and README.md are already LF; converting them is a no-op that must not corrupt them.

## Reference solution
1. bash: `find 文稿库 -type f | grep -v /win/ | xargs sed -i 's/\r$//'`
2. bash: `grep -rlc $'\r' 文稿库` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the four src files with CRLF now use LF; win/*.bat still use CRLF).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. 把 文稿库 下的文件换行符从 CRLF 统一改成 LF，win 目录里的批处理保持 CRLF，检查后回复 DONE。
2. 请去掉 文稿库 里除批处理之外的文件的回车符（\r），行尾只留 LF，参照 文稿库/README.md，完成后回复 DONE。
3. 批量 dos2unix：文稿库 目录下的 src 文件全部转 LF，win 里的 .bat 不动，改完核对并回复 DONE。
4. 文稿库 里的文本文件统一成 LF 换行，README 里要求保持 CRLF 的除外，确认后回复 DONE。
5. 清理文稿库目录的 Windows 换行，保留 win 文件夹原样，改完检查并回复 DONE。
