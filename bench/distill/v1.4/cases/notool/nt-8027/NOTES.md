## Traps
- None. 用户明确说别查，考的是 Git 的稳定概念。

## Reference solution
不调用任何工具，直接回答（1–2 句）：fetch 只把远端的最新提交下载到本地仓库，不动当前分支；pull 相当于 fetch 之后再把远端分支合并（merge）进当前分支。判据：零调用，包含 fetch 和「合并/merge」。

## Why the answer is unique
fetch 与 pull 的关系是 Git 的固定语义，答案唯一；管理手册与问题无关。
