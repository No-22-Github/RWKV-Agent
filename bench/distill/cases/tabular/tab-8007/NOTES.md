## Traps
- None.

## Reference solution
1. data_query：path 借阅/2026-09.csv，group_by 分馆，operation sum，field 册数。结果：城东分馆 126、北苑分馆 122、城西分馆 121、南湖分馆 96、中心馆 76。
2. write_file 报表/9月借阅汇总.csv，内容为表头「分馆,册数」加按册数降序的五行。
3. 回读 报表/9月借阅汇总.csv 确认内容。
终答一句话：已把 9 月各分馆借阅册数写到 报表/9月借阅汇总.csv（五个分馆，城东分馆 最多）。回复里不重复表格内容。判据：文件包含期望的表头与五行（顺序一致）；终答提到文件名。

## Why the answer is unique
五个分馆的合计互不相同，降序唯一；表头由题面指定。
