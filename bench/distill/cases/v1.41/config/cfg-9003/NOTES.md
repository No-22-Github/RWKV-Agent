## Traps
- TR-READONLY: 部署/归档/ also has 日志级别=debug; 部署/说明.md says archives stay byte-identical.

## Reference solution
1. bash: `find 部署 -name 服务.env | grep -v /归档/ | xargs sed -i 's/日志级别=debug/日志级别=info/'`
2. bash: `grep -rn 日志级别 部署` to confirm five services changed and the archive did not.
Final answer: 五个服务的 服务.env 都改成了 日志级别=info，行尾注释保留；归档目录没动。

## Why the answer is unique
Only the value changes; the trailing comment and the archive must stay as they are.
