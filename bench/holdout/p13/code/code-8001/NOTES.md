## Traps
- 无陷阱（L0）。要点：答案是一段 2–5 句的自然语言概览，必须落到 README、settings.json、app.py 三个文件的真实内容上：webhook 接收与转发、监听 8443、上游是 Kestrel Pay。泛泛而谈「这是一个支付服务」而不含这些事实的答案过不了判据。

## Reference solution
1. 读 README.md：Hookline 是卡支付 webhook 中继，校验签名后转发给内部计费服务（1 次调用）。
2. 读 settings.json：监听 8443，上游 https://api.kestrelpay.example/v2，retry_limit 3，auto_reconcile 关闭（1 次调用）。
3. 读 app.py：只处理 payment.captured 事件，按 retry_limit 重试转发，失败进 dead-letter（1 次调用）。
4. 终答（英文，自然语言 3–5 句，可含短列表）：用途 + 接线（端口 8443、上游 Kestrel Pay、计费服务）+ 配置行为（重试 3 次、自动对账未开）。

## Why the answer is unique
三个文件互相印证且无冲突：README 说明用途，settings.json 给出端口/上游/重试，app.py 给出事件过滤与转发路径。判据的三个必含事实（webhook、8443、Kestrel）分别只能来自对这三份材料的阅读；没有第二种「同样是概览但不含这些事实」的合格答法。
