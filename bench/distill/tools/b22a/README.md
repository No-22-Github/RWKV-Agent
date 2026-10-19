# b22a 出题脚本（v2.2：本地搜空 -> 上网，题号 34001–34090，work-v3 目录）

| 文件 | 内容 |
| --- | --- |
| `common.py` | 批次设置、`fx()` 网页 fixture、`T()` 单轮判据、`mk()` 写题（verify/NOTES）、日期写法 `dates()`、来源词表 `SRC` |
| `kit.py` | 三个子类的题型函数 `a1()` / `a2()` / `a0()`（工具约束、`max_calls`、判据都在这里统一） |
| `a1_x.py` `a1_y.py` `a1_z.py` `a1_w.py` | 34001–34040 A1：工作区有相关文件但不含答案，答案只在网页里 |
| `a2_x.py` `a2_y.py` | 34041–34065 A2：题面已说本地没有，第一步 web_search，不碰本地工具 |
| `a0_x.py` `a0_y.py` | 34066–34090 A0 对照：答案在工作区文件里，网页给的是另一个数，不该上网 |

判据：A1 `required_tools=[web_search]`、`max_calls {search_text:2, list_files:2}`（含"先本地后外部"的倒序多轮题放到 3）、`output_contains` 为网页独有的值，并要求终答带来源说法；
A2 `forbidden_tools=[list_files, search_text, read_file]`；A0 `forbidden_tools=[web_search, web_fetch]` + `output_excludes` 放网页上的另一个值（追问外部信息的第二轮不禁）。

```bash
cd bench/distill/tools/b22a && python3 build.py   # 无随机数，重跑逐字节一致；末尾打印分子类统计
```
