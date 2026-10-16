## Traps
- TR-ABSENT: backup_retention_days 在被问的范围内没有定义。
- TR-DECOY: settings.yaml 有 backup_schedule、backup_target，但保留天数写在 NAS 端，不在 ERP 配置里。

## Reference solution
读 settings.yaml 与 backup.md：配置里没有 backup_retention_days，文档说保留策略在 NAS 端。

## Why the answer is unique
ERP 配置里没有 backup_retention_days；backup.md 说明保留策略由运维在 NAS 端配置，要去 nas-02 上看。
