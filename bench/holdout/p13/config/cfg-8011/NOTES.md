## Traps
- TR-PRECEDENCE: upload_max_mb 在三层各有一个值——env-vars.txt 的 128、site.yaml 的 64、defaults.yaml 的 32。只看 site.yaml 会答 64，只看 defaults.yaml 会答 32；两个文件的首行注释写明了优先级，容器环境变量优先生效，正确答案是 128。

## Reference solution
1. 读 defaults.yaml 与 site.yaml，确认 upload_max_mb 有 32、64 两个候选值。
2. 读 env-vars.txt（首行注释声明它优先于另外两层）：upload_max_mb=128。
3. 生效值 128。

## Why the answer is unique
三个文件的首行注释构成一条完整的优先级链：环境变量 > 站点覆盖 > 默认值，upload_max_mb 在三层都出现，按链取最高层的 128 是唯一结果；64 与 32 分别是被覆盖的下层值，与注释声明的顺序矛盾。答案唯一为 128。
