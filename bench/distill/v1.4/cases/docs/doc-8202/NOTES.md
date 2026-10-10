## Traps
- 24 小时是避免硬食物的时间，不是禁食时间。

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：补牙后局麻没退之前别吃东西，大约要等 2 小时（常见问题/补牙后.md）；24 小时内还要避开过硬过黏的食物。
判据见 case.json（contains=[] any=['2 小时', '2 个小时', '2小时', '2个小时'] excl=[]）。

## Changelog
- v2：S5：题面加「诊所须知里」——原题面没有任何指向本地文件的线索，三遍老师都凭常识作答没读 FAQ。

## Why the answer is unique
禁食只到局麻消退，约 2 小时。
