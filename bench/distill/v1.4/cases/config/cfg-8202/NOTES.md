## Traps
- 草稿文件写了 30 人，但 README 说明未通过评审。

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：单车团课人数上限是 18 人（课程/团课.yaml）；草稿里的 30 人没有通过评审，不作数。
判据见 case.json（contains=[] any=['18 人', '18 位', '18 个人', '18人', '18位', '18个人'] excl=['上限是 30', '上限为 30', '最多 30', '最多30']）。

## Why the answer is unique
团课.yaml 是唯一正式文件；单车的上限在其中写明为 18。
