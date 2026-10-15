## Traps
- TR-NEARNAME: 用户写 `config/Settings.yml`，实际是 `config/settings.yaml`（大小写与扩展名）。读失败后放弃会答 UNKNOWN。
## Reference solution
1. read_file config/Settings.yml 失败（1）
2. list_files config（2）
3. read_file config/settings.yaml，port: 8472（3）。ref_calls=3。
## Why the answer is unique
config 下只有 settings.yaml 与 logging.yaml，后者与所问文件名不近；端口只在 settings.yaml 的 server.port 出现一次，8472。回答须提到 settings.yaml。

EXAM-CANARY-7be94d18
