## Traps
- TR-MULTISRC: local 文件自带覆盖说明。

## Reference solution
config.yaml 写 8080，config.local.yaml 写 9090 且声明覆盖前者。

## Why the answer is unique
读两个文件：local 覆盖，生效 9090，但要说明两处不一致。
