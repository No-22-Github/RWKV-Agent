## Traps
- 同名的 jpg 照片不是轨迹文件。

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：线路目录里一共有 4 条 gpx 轨迹：九溪、龙井、天目山和清凉峰；照片和备注不算。
判据见 case.json（contains=[] any=['4 条', '4 个', '4 份', '4条', '4个', '4份', '四条', '四个'] excl=[]）。

## Why the answer is unique
gpx 文件共 4 个。
