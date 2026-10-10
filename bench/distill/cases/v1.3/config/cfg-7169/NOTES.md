## Traps
- TR-PRECEDENCE / TR-SUPERSEDE: README 写明迁移完成后线上只读新文件 rental-api.json（免押 500），但 docs/release-notes.md 记录 2026-08-24 回滚后线上进程仍按旧配置的启动参数运行（旧值 300），切换窗口未定。「读新文件」的规范与「进程还带着旧参数」的记录矛盾，生效值无法确定。

## Reference solution
1. 读 README.md、config/rental-api.json、config/rental-legacy.json 和 docs/release-notes.md。
2. 新文件 500、旧文件 300，README 的迁移规范指向 500，发布记录的回滚说明指向 300。
3. 终答按 allocation v1.3 §4.1 第四行：说明给不出确定值、为什么（规范与回滚记录矛盾）、给替代。参考措辞：「线上生效的免押额度现在给不出确定值：rental-api.json 按迁移规范应该是 500，但 release-notes 记录 8 月 24 日回滚后线上进程仍按旧配置的启动参数跑，旧文件里是 300，切换窗口未定。客服规范里建议两个值先都不写死，等财务核对完统一切换后再更新；对外口径可以先按 300 承诺、标注以切换后为准。」判分用 output_contains_any（键名、deposit free limit 或「免押额度」）；两个数值都是答案要引用的内容，output_excludes 只排除 UNKNOWN 与「我没有工具」类说法。

## Why the answer is unique
README 的迁移规范与 release-notes 的回滚记录直接冲突：规范说只读新文件、记录说进程仍带旧参数，两份证据各支持一个值且都无法被另一份推翻，唯一站得住的答案是指出矛盾并给下一步。任何单值答案都与至少一份记录相抵，题面也没有给出能裁决的第三份材料。
