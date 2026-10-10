## Traps
- The security/ exception needs 3.

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：An ordinary pull request needs 2 approvals (guides/review-rules.md); only changes under security/ need 3.
判据见 case.json（contains=[] any=['2 approvals', 'two approvals', 'Two approvals'] excl=[]）。

## Changelog
- v2：S5：判据由 token「2」改为 any「2 approvals / two approvals」——老师写 Two approvals 被判挂。

## Why the answer is unique
The word ordinary points at the general rule: 2.
