## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
turn1 read_file 读预算表；turn2 web_fetch 长页面 -> read_file 跳到价格章节；turn3 算总价；turn4 与第一轮预算比较，差额 42

## Why the answer is unique
The last turn compares the web price total with the budget read in the first turn.

## Estimated trajectory tokens
10144
(fixture: kelpwave-cloud.example/pricing/compute=5831)


## Five alternative phrasings of the task
1. Our compute budget sheet is infra/q4-compute-budget.csv. What is the monthly budget line for the general-purpose 4 vCPU instance?
2. 麻烦帮我：Our compute budget sheet is infra/q4-compute-budget.csv. What is the monthly budget line for the general-purpose 4 vCPU instance?
3. Our compute budget sheet is infra/q4-compute-budget.csv. What is the monthly budget line for the general-purpose 4 vCPU instance? (keep it organised)
4. 想请你看看：Our compute budget sheet is infra/q4-compute-budget.csv. What is the monthly budget line for the general-purpose 4 vCPU instance?
5. 再确认一下：Our compute budget sheet is infra/q4-compute-budget.csv. What is the monthly budget line for the general-purpose 4 vCPU instance?
