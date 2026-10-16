## Traps
- TR-MULTISRC: 覆盖文件声明优先并带日期。

## Reference solution
log.yaml 写 info，应急覆盖文件写 debug 并声明优先。

## Why the answer is unique
读两个文件：生效 debug，并提示这是临时覆盖与基础配置不一致。
