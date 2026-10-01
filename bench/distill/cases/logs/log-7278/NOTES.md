## Traps
- TR-ABSENT / TR-MULTISRC: 两份日志里都没有 EXPORT_MEMBER_LIST。诱饵是审计日志里的 2 条 EXPORT_SUMMARY（报表导出，带操作人与文件名）：只看 audit 的人会答「导出过 2 次」，只看 app 的人会拿 JOB_DONE 的报表生成当导出证据——每个来源单独看都给得出像样的错答案，只有两份都查过、且分清 EXPORT_SUMMARY 与 EXPORT_MEMBER_LIST 是两种事件，才能得出「没有发生过」。

## Reference solution
1. 读 README.md 分清两份日志的分工，再分别读 logs/audit-2026-09-10.jsonl 与 logs/app-2026-09-10.jsonl。
2. 审计日志里只有 2 条 EXPORT_SUMMARY（日报与理赔报表），应用日志里只有报表生成任务；两份日志都没有 EXPORT_MEMBER_LIST。
3. 终答两到三句（allocation v1.3 §4.1 第一行）：查了哪两份日志、事件零记录、点名相近事件并说明为什么不算、给下一步。参考措辞：「app 和 audit 两份日志都查过了：9 月 10 日没有 EXPORT_MEMBER_LIST 事件，会员名单没有导出记录。审计里最接近的是 zhang.wei 和 li.na 的两条 EXPORT_SUMMARY，但那是日报和理赔报表，不是会员名单。如果合规组要留档，可以把这两份日志的核对结论直接写进台账。」判分用 output_contains_any（事件名、「会员名单导出」或 member list）。

## Why the answer is unique
README 写明导出行为只记在审计日志的 EXPORT_* 事件里、应用日志只记任务结果，两份日志合起来才是当天行为的完整证据面，所以事件名两处都不出现就是没有发生。诱饵是 EXPORT_SUMMARY：它与被问事件同属导出族、还带操作人，把它当成会员名单导出正是本题要卡的错误——单看一个来源必错，两份都查清才能落到「没有」。
