## Traps
- TR-ABSENT: smtp_port 在被问的范围内没有定义。
- TR-DECOY: app.ini.sample 里的 587 只是示例，不是实际配置。

## Reference solution
读 app.ini：[mail] 有 smtp_host 无 smtp_port；sample 的 587 是样例。

## Why the answer is unique
app.ini 里只配了 smtp_host 与 sender，没有 smtp_port；587 出现在 app.ini.sample（示例文件），不能当成实际值。
