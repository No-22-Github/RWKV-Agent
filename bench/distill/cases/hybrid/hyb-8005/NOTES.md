## Traps
- None.

## Reference solution
1. 读 采购/均价.md：2025 年 8 月均价 4860 元/批。
2. 搜索并抓取统计局 2026 年 8 月 CPI 页面：同比上涨 2.3%。
3. calculator：4860 * 1.023，precision 2 → 4971.78。
终答一句话：按 8 月 CPI 同比 2.3% 调整后约 4971.78 元/批（4860 × 1.023）。判据：包含 4971.78（可去尾零），调用过 calculator。官方统计页的搜索摘要已经给出同比 2.3%，直接用摘要也可以，不强制抓取全文。

## Why the answer is unique
基数与涨幅各只有一个来源。

## Changelog
- v2：去掉 required_tools 里的 web_fetch。本题考的是计算器（M8），官方统计页的搜索摘要已写明同比 2.3%，试跑里解题者凭摘要计算是合理路径。

## Five alternative phrasings of the task
1. 2026 年 8 月 CPI 同比
2. 国家统计局 8 月 CPI 2026
3. CPI 同比涨幅 2026年8月
4. 2026 August China CPI year on year
5. 居民消费价格指数 CPI 8 月
