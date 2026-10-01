## Traps
- TR-DECOY: deploy.env 末行有一行被注释的「# 灰度发布: 按流量 5%（待安全评审，暂未启用）」，扫一眼像已配置；以 # 开头的行不生效。把它当已配置会答「灰度发布已开启（5%）」，判据里的 output_excludes 会拒掉这种说法。

## Reference solution
1. 读 配置基线.csv：必填项为 server_port、db_pool_size、慢查询日志、灰度发布、log_level。
2. 读 app.yaml 与 deploy.env：生效配置覆盖前四项；灰度发布只出现在 deploy.env 的注释行里，未生效。
3. 回答：缺「灰度发布」；没有生效值——基线要求显式配置，env 里那行被注释、未启用。

## Why the answer is unique
必填项与两处生效配置的差集只有灰度发布一项，这是夹具事实；被注释的行在 env 语法上不生效，「已开启」的说法与文件内容直接冲突。合格的回答要点名灰度发布这一项并说明它没有生效值。
