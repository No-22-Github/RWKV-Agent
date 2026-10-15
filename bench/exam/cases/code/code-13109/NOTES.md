## Traps
- TR-DECOY: 同文件里还有 calc_discount_rate（另一个函数），被 src/promo/rules.py 调用；src/report/summary.py 只在注释里提到 calc_discount，不是调用。把 rules.py、summary.py 算进调用方都错。
- 第 2 轮依赖第 1 轮：“它”指 calc_discount。判分要求两个真实调用方 cart.py、render.py 都出现（token 匹配）。说明：不对 rules.py、summary.py 设 output_excludes，因为好回答可能写“rules.py 用的是 calc_discount_rate，不算”；复核时请读回答确认没有把它们当成调用方。

## Reference solution
1. search_text calc_discount（1 步），看出定义在 src/pricing/discount.py。
2. 第 2 轮：根据搜索结果判断 cart.py、render.py 是调用，rules.py 调的是 calc_discount_rate，summary.py 只是注释（0–2 步）。共 2–3 步。

## Why the answer is unique
调用 = 代码里出现 `calc_discount(`（非注释、非定义）。仅 cart.py 与 render.py 满足。

EXAM-CANARY-3358520d
