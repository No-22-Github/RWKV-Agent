## Traps
- Undo: the change from turn 1 is already on disk (user accepted it); reverting needs the earlier content, restoring too much or too little fails.

## Reference solution
三处换占位符；之后 db 恢复为原值 pg-8821-xq，其余保持 CHANGEME。

## Why the answer is unique
Turn 1 makes the edit; turn 2 reverts all or part of it; final files equal expect.files (rules are relative to the initial fixture).

## Five alternative phrasings of the task
1. 把配置.ini 里三个 password 的值都换成占位符 CHANGEME，我要提交到公开仓库。
2. 麻烦问下：把配置.ini 里三个 password 的值都换成占位符 CHANGEME，我要提交到公开仓库。
3. 把配置.ini 里三个 password 的值都换成占位符 CHANGEME，我要提交到公开仓库。（简单说就行）
4. 你好，把配置.ini 里三个 password 的值都换成占位符 CHANGEME，我要提交到公开仓库。
5. 还有件事：把配置.ini 里三个 password 的值都换成占位符 CHANGEME，我要提交到公开仓库。
