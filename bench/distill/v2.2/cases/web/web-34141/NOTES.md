## Traps
- 必须同时读网页和本地文件，只看一边答不全。

## Reference solution
web_fetch + read_file -> body 25>10、rate 1500>1200 超标，connections 150<200 正常

## Why the answer is unique
两项超标：max_body_mb、rate_per_min。

## Five alternative phrasings of the task
1. 按 https://dev.stratoscale.example/docs/limits 上的新规，检查一下 config/limits.yaml 有没有超标的项。
2. 想确认一下：按 https://dev.stratoscale.example/docs/limits 上的新规，检查一下 config/limits.yaml 有没有超标的项。
3. 按 https://dev.stratoscale.example/docs/limits 上的新规，检查一下 config/limits.yaml 有没有超标的项。（简单说就行）
4. 麻烦帮我看看：按 https://dev.stratoscale.example/docs/limits 上的新规，检查一下 config/limits.yaml 有没有超标的项。
5. 再问一件事：按 https://dev.stratoscale.example/docs/limits 上的新规，检查一下 config/limits.yaml 有没有超标的项。
