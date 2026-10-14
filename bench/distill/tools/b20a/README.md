# b20a 出题脚本（v2.0：缺工具·本地动作，题号 20001–20040）

| 文件 | 内容 |
| --- | --- |
| `common.py` | 批次设置、中英"做不了"词表与假完成词表、fixture sha256 守卫、sidecar 参考解回读 |
| `refuse.py` | "做不了"题构建器（bash never_offer，expect.files 保证原文件不变/目标不存在） |
| `ctl.py` | 对照题构建器：`do_case`（bash 真做完）与 `missing_case`（命令不存在，exit 127 如实说明） |
| `r_delete.py` 20001–20007 | 删文件/目录（含先做能做的部分：求大小、数文件、列未引用脚本） |
| `r_move.py` 20008–20012 | 移动/改名（write_file 另存不算完成） |
| `r_run.py` 20013–20026 | 运行脚本/npm/make/pytest、git、装包、chmod |
| `c_ctl.py` 20027–20040 | 对照题：9 道 bash 做完，5 道 python3/git/npm/make/pip 缺失 |

```bash
cd bench/distill/tools/b20a && python3 build.py      # 写 40 题，并在 just-bash sidecar 里回放 14 条 bash 参考解
python3 build.py --no-sidecar                        # 无 sidecar 时全部标 UNVERIFIED
```

无随机数，重跑逐字节一致。词表为区分大小写的子串匹配，所以中英大小写写法都列了。
