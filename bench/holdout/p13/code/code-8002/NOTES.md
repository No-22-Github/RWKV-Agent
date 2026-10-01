## Traps
- 无陷阱（L0）。要点：答案是一段 2–5 句的中文自然语言说明，必须落在脚本与配置的真实行为上：打包 uploads 目录、按 keep_versions 保留最近 7 份、按 schedule（02:30）定时跑、产物拷到 /mnt/nas/backups。只说「这是个备份脚本」而给不出这些事实的答案过不了判据。

## Reference solution
1. 读 tools/backup.py：读 config/settings.json，把 source_dir 打成 tar.gz，删掉超出 keep_versions 的旧包，再拷到 target（1–2 次调用）。
2. 读 config/settings.json：uploads、7 份、02:30、/mnt/nas/backups（1 次调用）。
3. 终答（中文，自然语言 3–5 句）：脚本每天 02:30 把 uploads 打成快照包，本地只留最近 7 份，并把最新包拷到 /mnt/nas/backups。

## Why the answer is unique
脚本与配置一一对应：source_dir=uploads 决定打包对象，keep_versions=7 决定保留策略，schedule=02:30 决定节奏，target 决定落盘位置，代码里没有其他分支或第二数据源。判据的三个必含事实（uploads、keep_versions、02:30）只能来自读完这两份材料；漏读配置就说不全保留与节奏。
