## Traps
- TR-NOTOOLNEED: a how-to question that names a real directory but asks for a command to run later, not now.

## Reference solution
No tool call. Final answer: `find 备份 -name '*.sql.gz' -mtime +7 -print` 先列出确认，再把 -print 换成 -delete；并提醒先核对列表再删。

## Why the answer is unique
The user said not to execute; any tool call (even listing the directory) violates the request.
