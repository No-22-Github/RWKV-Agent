## Traps
- TR-DECOY: @张三丰 starts with @张三; matching `@张三` without the trailing space gives 242. 会议纪要/README.md says they are different people.
- TR-DEFN: finished items (`[x]`) are not outstanding; counting every @张三 line gives 185.
- TR-MULTISRC: 18 meeting files in three month folders; October alone gives 46.

## Reference solution
1. bash: `cat 会议纪要/*/*.md | grep -c '^- \[ \] @张三 '`
Final answer: 张三名下还有 117 条未完成的待办（只算「- [ ] @张三 」，不含已完成项和 @张三丰）。

## Why the answer is unique
The open marker and the full assignee token (with the following space) are literal parts of every line.
