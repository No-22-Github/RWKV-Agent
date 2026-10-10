## Traps
- 东滩站文件只覆盖采样秒，报警温度要回退到全局。

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：东滩站没有单独设置，沿用全局的 75 度（电站/全局.ini）；西坡站才是 68 度。
判据见 case.json（contains=[] any=['75 度', '75度', '75 ℃', '75℃', '75°C', '75 °C'] excl=[]）。

## Why the answer is unique
东滩站无报警温度项，取全局 75；西坡站的 68 属于另一站点。
