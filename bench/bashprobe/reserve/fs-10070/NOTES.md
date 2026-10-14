## Traps
- TR-DECOY: counting every *.md including the folder READMEs gives 88; the README's rule gives 82.
- 179 files in nested folders under 文档/, so counting by listing is not practical.

## Reference solution
1. bash: `find 文档 -type f -name '*.md' ! -name 'README.md' ! -name '统计口径.md' | wc -l` -> 82
Final answer: 正文文档共 82 篇（不含各目录 README.md 和 .md.bak）。

## Why the answer is unique
The README fixes which names count; matching by that rule over the whole tree gives one number.
