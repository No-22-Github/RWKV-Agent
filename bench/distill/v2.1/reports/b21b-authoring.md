# b21b 出题报告（31101-31175，75 题）

- 子类：查完写汇总 20、按格式生成 12、多轮反馈修改 18、撤销重做 10、复合请求 15（建议值不变）。
- 场景：tabular / logs / config / docs / hybrid（undo 5 题与复合 15 题放 hybrid，其余按内容分）。
- 中文 67/75（89%）；多轮（≥2 用户轮）31/75（41%）；L0 4 题（5%），L1 68，L2 3；原因：大多数题带 1 个陷阱标签。
- tool_policy：全部只写 must_offer，每题都含完整通过路径（读+写）。分布：read_file+write_file 15、read_lines+write_file 15、bash 15、read_file+write_file+append_file 10、search_text+read_file+write_file 10、read_lines+replace_lines 5、read_file+replace_lines 5（后两种仅用于原地改文件的题）。
- 判据：`expect.files` 用 equals 精确判新文件/最终文件，其余无关文件 unchanged；复合题终答另加 `output_contains`（计数类用带上下文的 `output_contains_any`，不用单个数字）；31148 末轮致谢不应调工具。所有 equals 含末尾换行，题面按需写明格式（缩进、小数位、制表符等）。
- verify.py：嵌入各题 compute()，从 fixture 重算最终文件；fixture sha256 固定。
- 自检：build.py 连跑两次逐字节一致；gate `*-311[0-7]?`：lint 0 违规，verify 75/75；loadcheck 300 题全部加载。
- 已知风险：equals 对末尾换行、JSON 浮点/缩进敏感（老师写出等价但字节不同会判错）；撤销题依赖对话历史里记得原内容；31102 等少数题多个合理排序没写满规则；部分题的读工具是 read_lines 或 bash，老师要换工具完成。
- 老师最可能答错：tab-31146（积分榜两步改规则）、tab-31128（带 + 号的金额与累计余额）、doc-31126（拆条目格式很多细节）、hyb-31159（改写后要精确还原原文并只加一小段）、doc-31141（排序规则含 Unicode 字典序，且要删项）。
