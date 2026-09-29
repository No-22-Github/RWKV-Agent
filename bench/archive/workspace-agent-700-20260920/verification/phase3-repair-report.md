# Phase-3 修复与 700 条导出

2026-09-20。用户要求修复而不重出题，并允许少量重复。原 18 条未批准记录已全部处理：
7 条修复内容或标签；13 条重复记录按显式授权保留（其中 2 条同时修了标签，故总共 18 条）。

## 实际修复

- ws7-cfg-0004-b31：任务明确只修改 deploy/billing.yaml 的 grpc_port，其他文件与字段保护；修正 oracle 中错误的唯一性说明，判据保护全部输入文件。
- ws7-doc-0004-b20：删除产物及 equals 中规格未要求的空白行，得到标题紧接三条列表的四行卡片。
- ws7-hyb-0001-b12：web_fetch 前加入真实 web_search；URL 在前序回执可见，独立计算 (440+550+660)/2.2*0.95=712.50。
- ws7-scr-0003-b33：隐藏输入新增窗口内 failed、窗口前成功、窗口后成功三行；正确输出不变，分别移除状态、下界、上界过滤的三种错误脚本均被真实执行判据拒绝；保护全部可见输入。
- ws7-web-0002-r20、ws7-web-0001-b31、ws7-web-0004-b31：补 no_tool_closeout 标签。

7 条均创建全新逐步 init/call/finish 会话，再由 rebuild_records.py 重建、验证并重新绑定。
旧 sketches、records、说明文件保存在 evidence/revisions/phase3-repair-20260920/；旧 sessions 保留。

## 保留与审查身份

13 条近重复的限定清单见 phase3-retention-policy.json。仅允许训练集内已知结构相似与数据复用；
不放宽内容正确性、真实回执、输出契约、精确内容去重和跨 split 隔离。未重写题目以制造差异。
700 是记录数，不是 700 个结构独立任务。

本轮 18 条最终决定如实标为 agent:phase3-repair-main / production，不冒充修复后的独立审查。
682 条原独立批准记录继续保留。独立覆盖：36 锚点、70 验证、576 非锚点训练记录。
原拒绝结论及证据保存在追加式 review-log.jsonl 与修复前快照。

## 验证与结果

- 18 条全新 verify_one：回放、回执、产物哈希、契约、当前 ledger 全部通过，见 phase3-repair-replays.jsonl。
- 定向正反例与独立复算全部符合预期，见 phase3-repair-checks.json。
- negative_tests.py：全部反例被对应门槛拒绝，正例对照通过；未放宽任何执行门槛。
- build_corpus.py：700 candidates / gate_passed / approved / exported；pending=0，train=630，validation=70。
- reverify.py：349/349 要求额外回放的记录通过，failed=0，missing_binding=0。
- 实际 token：p50=1847，p90=2487，p99=3006，max=3352 <= 4096。
- 精确内容重复=0；未解决跨 split 近重复=0；同组跨 split=0。
- make_acceptance_report.py：全部硬门槛为 true，状态 data_ready（按用户更新后的近重复口径）。

未启动训练；数据正确性与模型训练收益为不同结论。其余历史已知局限继续在 acceptance-report 中披露。
