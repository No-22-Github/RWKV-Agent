## Traps
- TR-DECOY: deploy.env 末行有一行被注释的 sms_api_key（# sms_api_key=等安全组下发后放开），扫一眼像已配置；以 # 开头的行不是生效配置。把它当已配置会答「无缺失」。

## Reference solution
1. 读 配置基线.csv：必填项为 server_port、db_pool_size、cache_ttl_seconds、sms_api_key、log_level、session_ttl_hours。
2. 读 deploy.env：生效行覆盖其中五项；sms_api_key 只出现在被注释的行里。
3. 缺的是 sms_api_key。

## Why the answer is unique
基线六个必填项与 env 生效行（注释行除外）逐一对比，差集只有 sms_api_key，结果是唯一的；注释行在 env 语法上不生效，把它计成已配置的「无缺失」与 env 文件的既有语义矛盾。答案唯一为 sms_api_key。
