## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
 一次 web_fetch 同时取 2 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
write_file 写入 gym-compare.md
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
14653
(fixture: liyun-gym.example/membership/price=5163, fenghuo-fit.example/join/plans=5090)


## Five alternative phrasings of the task
1. 帮我对比力云健身和烽火运动馆的会员价格，页面是 https://liyun-gym.example/membership/price 和 https://fenghuo-fit.example/join/plans 。年卡、私教、暂停和转让都要有，结果存到 gym-compare.md。
2. 麻烦帮我：帮我对比力云健身和烽火运动馆的会员价格，页面是 https://liyun-gym.example/membership/price 和 https://fenghuo-fit.example/join/plans 。年卡、私教、暂停和转让都要有，结果存到 gym-compare.md。
3. 帮我对比力云健身和烽火运动馆的会员价格，页面是 https://liyun-gym.example/membership/price 和 https://fenghuo-fit.example/join/plans 。年卡、私教、暂停和转让都要有，结果存到 gym-compare.md。（用中文回答）
4. 想请你看看：帮我对比力云健身和烽火运动馆的会员价格，页面是 https://liyun-gym.example/membership/price 和 https://fenghuo-fit.example/join/plans 。年卡、私教、暂停和转让都要有，结果存到 gym-compare.md。
5. 再确认一下：帮我对比力云健身和烽火运动馆的会员价格，页面是 https://liyun-gym.example/membership/price 和 https://fenghuo-fit.example/join/plans 。年卡、私教、暂停和转让都要有，结果存到 gym-compare.md。
