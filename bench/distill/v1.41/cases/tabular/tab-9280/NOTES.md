## Traps
- TR-READONLY: 客户/导出模板.csv keeps its header. TR-DECOY: the header 「备用手机」 contains 手机 (a global `s/手机/手机号/` renames it too); only the header line changes, never the data rows.
- Turn 3 undoes both earlier turns: all headers end as in the fixture.
- Turn 2 changes part of what turn 1 did, so the final state is not a plain replace-everywhere; turn 3 undoes the whole change.

## Reference solution
Turn 1:
1. bash: `find 客户 -name '*.csv' | grep -v 导出模板 | xargs sed -i '1s/,手机,/,手机号,/'`
2. bash: `head -n 1 -q 客户/*.csv`
Final answer: DONE (四个区域表的表头是手机号).
Turn 2:
1. bash: `sed -i '1s/,手机号,/,手机,/' 客户/华东.csv 客户/西南.csv`
2. bash: `head -n 1 -q 客户/*.csv`
Final answer: DONE (华东、西南回到手机，华北、华南是手机号).
Turn 3:
1. bash: `find 客户 -name '*.csv' | xargs sed -i '1s/,手机号,/,手机,/'`
2. bash: `head -n 1 -q 客户/*.csv`
Final answer: DONE (所有表头都是手机).

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. 把各区域客户表的表头手机改为手机号，华东西南改回，最后全部撤销
2. 表头「手机」→「手机号」（模板和备用手机除外），局部还原后整体恢复
3. 先统一改表头，再让华东西南回旧表头，最后所有文件回到初始表头
4. 客户 CSV 表头改名，两个文件还原，再把剩下的也还原
5. Rename the phone header in the customer sheets, restore two, then restore all headers to the originals.
