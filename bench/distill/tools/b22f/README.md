# b22f 出题脚本（v2.2：8–16K token 长任务，work-v3，题号 34501–34580）

| 文件 | 内容 |
| --- | --- |
| `common.py` | 批次设置、`mk()` 写题（verify/NOTES）、`est()` token 估算（按 `rwkv-lab tokcount` 校准：汉字约 1.15 token/字，其余约 4.9 字符/token） |
| `gen.py` | 固定种子的填充文字引擎（章节段落、导航、相关阅读、评论、页脚；填充句不含数字，数字只来自手写事实） |
| `pages.py` | `page()` 拼长网页；`trajectory()` 轨迹 token 估算（BASE=1500、web_fetch 长页返回约 1400，均为重放实测） |
| `f1.py` `f1a–e.py` | F1 长网页摘要/报告 34501–34530（9 题带第二轮追问，14 题写文件） |
| `f2.py` `f2a–d.py` | F2 多网页对比 34531–34550（2–3 页，合计 ≤ 12000 token） |
| `f3.py` `f3a–b.py` | F3 多份 400–1200 行登记簿汇总 34551–34565（只有「级别高且未关闭」组合算数，其余字段组合都是干扰） |
| `f4.py` `f4a–c.py` | F4 长多轮 34566–34580（预算表+网页报价、两站点 12 个月总价、配置改值、长制度手册） |
| `measure.py` | 不属于构建：用 `rwkv-lab tokcount` 统计每题 fixture 的真实 token |

```bash
cd bench/distill/tools/b22f && python3 build.py    # 固定种子，重跑逐字节一致
python3 measure.py                                 # 真实 token 统计
```

`build.py` 开头的 `clean()` 只删除匹配 `^[a-z]+-345(01..80)$` 的目录（本批自己的题号），不动任何场景目录或别的批次。
