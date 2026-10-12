## Traps
- TR-READONLY: lib/vendor is third-party code and gets no header. The exact header text is only in lib/README.md.
- Turn 2 changes part of what turn 1 did, so the final state is not a plain replace-everywhere.

## Reference solution
Turn 1:
1. bash: `find lib -name '*.js' | grep -v /vendor/ | xargs sed -i '1i // 版权所有 2026 星河科技'`
2. bash: `head -n 2 -q lib/*/*.js`
Final answer: DONE (七个源文件第一行已加声明，vendor 未动).
Turn 2:
1. bash: `sed -i '1{/^\/\/ 版权所有 2026 星河科技$/d}' lib/gen/schema.js lib/gen/client.js`
2. bash: `head -n 2 -q lib/*/*.js`
Final answer: DONE (gen 下两个文件无声明，其余五个有).

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. lib 里的源码文件头部统一补上版权行（第三方除外），生成文件之后再去掉
2. 按 README 的版权声明给 js 文件加首行，vendor 不加；gen 目录两个文件撤销
3. 给 lib 的 js 批量加头部声明，然后 gen 里的不要
4. 添加版权头（除 vendor），再移除 gen/schema.js 和 gen/client.js 上的
5. Add the copyright line to the lib sources, skip vendor, then remove it from the generated files.
