# 清洗数据交付

新增精选 460 条（train 359 / validation 101）；可选混合集 1011 条（train 910 / validation 101），包含旧集当前可用的 551 条。

- 完整包：`outputs/workspace-agent-distill-clean-20260926.zip`
- 数据与说明：`outputs/workspace-agent-distill-clean-20260926/`
- 新增训练输入：`new-only/textonly/train.jsonl`；带 mask 的版本在 `new-only/rendered/`。
- 混合训练输入：`state-tune-textonly/train.jsonl`；带 mask 的版本在 `generated/rendered/none-ctx4096/`。
- 逐行决定：包内 `verification/selection-ledger.jsonl`，覆盖全部 1586 行。
- 全包异地解压、复建、oracle 和完整性检查通过。

ZIP SHA256：`676393e4bfd60e64ccd145f7c0385232e29c4540cfe5b82b2080ddb76ad191da`。

本目录保存便于仓库审阅的清洗报告与策略副本；报告中的相对数据路径以 ZIP 包根目录为准。完整原始输入和可执行清洗程序随 ZIP 提供。outputs 为 gitignored，本次未提交或推送，也没有运行训练。
