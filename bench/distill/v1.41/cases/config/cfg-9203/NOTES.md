## Traps
- TR-READONLY: jobs/nightly.toml is managed by ops (jobs/README.md).
- TR-DECOY: max_retries = 3 and the [alert] section's own `retries = 3` look the same; only the top-level key changes.

## Reference solution
1. bash: `find jobs -name '*.toml' | grep -v nightly.toml | xargs sed -i '/^\[/,$!s/^retries = 3$/retries = 5/'`
2. bash: `grep -rn retries jobs` to confirm the target files changed and the protected ones did not.
Final answer: DONE (sync, report, cleanup and export have retries = 5; nightly.toml, max_retries and the [alert] retries are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. 把 jobs/*.toml 顶层的 retries = 3 全部改为 5，README 里提到的例外别碰，检查后回复 DONE。
2. 各任务配置里的重试次数 retries 从 3 调到 5（只改顶层那一项），按 jobs/README.md 排除不该改的，完成后回复 DONE。
3. jobs 下的 toml，retries 改成 5，max_retries 和 [alert] 里的不动，nightly 也不动，核对后回复 DONE。
4. 批量把任务配置的 retries 由 3 提高到 5，注意 README 的说明，改完确认并回复 DONE。
5. 请更新 jobs 里托管之外的所有 .toml：顶层 retries 设为 5，其余保持原样，检查完回复 DONE。
