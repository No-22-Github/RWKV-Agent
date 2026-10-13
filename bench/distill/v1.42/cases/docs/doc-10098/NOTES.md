## Traps
- TR-READONLY: 版本记录.md keeps the old address.
- The :8080 backup URL starts with the same host; the pattern with /kb right after the host leaves it alone.
- 6 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find 手册 -name '*.md' ! -name 版本记录.md ! -name 说明.md | xargs sed -i 's#http://intranet\.xinghe\.local/kb#https://kb.xinghe.cn#g'`
2. bash: `grep -rn 'intranet\|kb.xinghe' 手册`
Final answer: 六篇手册里的知识库地址已换成 https://kb.xinghe.cn，版本记录和 8080 备用地址没动，grep 检查过。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
