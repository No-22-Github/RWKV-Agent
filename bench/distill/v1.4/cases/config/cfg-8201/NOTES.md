## Traps
- 默认文件里是 20 分钟，大棚 B 自己覆盖为 12 分钟。

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：大棚 B 每次灌溉 12 分钟：灌溉/大棚B.yaml 覆盖了默认的 20 分钟，一天灌 4 次。
判据见 case.json（contains=[] any=['12 分钟', '12 min', '12 分', '12分钟', '12min', '12分'] excl=[]）。

## Why the answer is unique
大棚 B 文件显式写了单次时长，覆盖默认值；大棚 C 的 15 分钟属于另一个大棚。
