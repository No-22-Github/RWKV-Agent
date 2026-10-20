## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
 一次 web_fetch 同时取 2 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
write_file 写入 loan-compare.md
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
14807
(fixture: haixin-bank.example/loan/personal-rates=5225, lixin-bank.example/product/xiaofei-dai=5182)


## Five alternative phrasings of the task
1. 帮我比较海信银行和立信银行的消费贷款，产品页分别是 https://haixin-bank.example/loan/personal-rates 和 https://lixin-bank.example/product/xiaofei-dai ，把利率范围、额度、提前还款和费用写成对比表，放到 loan-compare.md。
2. 麻烦帮我：帮我比较海信银行和立信银行的消费贷款，产品页分别是 https://haixin-bank.example/loan/personal-rates 和 https://lixin-bank.example/product/xiaofei-dai ，把利率范围、额度、提前还款和费用写成对比表，放到 loan-compare.md。
3. 帮我比较海信银行和立信银行的消费贷款，产品页分别是 https://haixin-bank.example/loan/personal-rates 和 https://lixin-bank.example/product/xiaofei-dai ，把利率范围、额度、提前还款和费用写成对比表，放到 loan-compare.md。（用中文回答）
4. 想请你看看：帮我比较海信银行和立信银行的消费贷款，产品页分别是 https://haixin-bank.example/loan/personal-rates 和 https://lixin-bank.example/product/xiaofei-dai ，把利率范围、额度、提前还款和费用写成对比表，放到 loan-compare.md。
5. 再确认一下：帮我比较海信银行和立信银行的消费贷款，产品页分别是 https://haixin-bank.example/loan/personal-rates 和 https://lixin-bank.example/product/xiaofei-dai ，把利率范围、额度、提前还款和费用写成对比表，放到 loan-compare.md。
