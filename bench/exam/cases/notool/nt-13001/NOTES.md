## Traps
无陷阱（L0）。工作区里的待办.md只是引诱模型先翻文件。

## Reference solution
0 次调用，打个招呼并概括能做的事（读写工作区文件、查网页、算数、查天气等）。

## Why the answer is unique
闲聊没有唯一答案。只判零调用（`tools: []` + `require_active_no_call`）和有回答。

## Scoring boundary
与 bank lint 冲突：lint 要求 smalltalk 的 output_contains_any 非空，但作者不为过 lint 硬塞关键词，见报告。

EXAM-CANARY-48852c6f
