## Traps
- TR-DECOY: the user names one file; a backup, old, example or other-environment copy carries a different value (2525).

## Reference solution
1. read_file on the named file.
Final answer: 生产环境的 SMTP_PORT 是 465（staging 用的是 2525）。

## Why the answer is unique
The user names the file; only it holds the current value. The copy with another value is a decoy.
Why bash is not the tool here: one named file and one fact, the read tool is the direct read. The turn forbids bash so rows teach that bash being offered does not make it the default.

## Five alternative phrasings of the task
1. 生产环境发邮件用哪个端口？看 env/prod.env。
2. env/prod.env 配的 SMTP 端口号是多少？
3. prod.env 里的 SMTP_PORT 值是？
4. 告诉我 env/prod.env 里 SMTP_PORT 的值。
5. 线上邮件服务器端口是多少，以 env/prod.env 为准？
