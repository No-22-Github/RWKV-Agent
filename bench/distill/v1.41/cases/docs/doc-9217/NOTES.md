## Traps
- TR-READONLY: docs/变更记录.md is a historical record; docs/README.md explains the rule and quotes the old term (docs/README.md).
- TR-DECOY: README.md itself contains 旧网关 inside its explanation and must not be rewritten.

## Reference solution
1. bash: `find docs -name '*.md' | grep -v -E '变更记录|README' | xargs sed -i 's/旧网关/边缘网关/g'`
2. bash: `grep -rn 旧网关 docs` to confirm the target files changed and the protected ones did not.
Final answer: DONE (overview, deploy, troubleshooting and monitoring use 边缘网关; the changelog and README still say 旧网关).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. 把 docs 下文档里的「旧网关」全部换成「边缘网关」，变更记录和 README 不改，检查后回复 DONE。
2. 术语更新：docs 目录里的正文用「边缘网关」替代「旧网关」，历史记录保持原样，完成后回复 DONE。
3. 批量替换 docs/*.md 里的旧网关为边缘网关，按 docs/README.md 的说明排除例外，核对后回复 DONE。
4. 请统一 docs 的叫法：旧网关 → 边缘网关，只改正文页面，改完确认并回复 DONE。
5. docs 里除了变更记录和说明文件之外，所有出现「旧网关」的地方都改成「边缘网关」，检查后回复 DONE。
