## Traps
- TR-NEARNAME: 断链 pages/flower-course.md 有近似名文件 pages/flower-course-v2.md 在场（那是未发布的新版草稿）；把它当成目标在场会少算一条。
- TR-DATEFMT: 斜线日期按站点备注为 月/日/年：04/10/2026 是 4 月 10 日（目标在场，不计），10/04/2026 是 10 月 4 日（不在四月窗口）。把 10/04/2026 误读成 4 月 10 日会把断链 pages/autumn-market.md 计入，得 3。

## Reference solution
1. 读取 官网页面清单.csv，按站点备注的约定解析上线日期，取 2026 年 4 月的页面：花艺课程、春季企划、媒体资料、花艺养护、秋日市集（10/04/2026 实为 10 月 4 日，不在窗口）。
2. 读取 站点备注.md 确认日期约定与路径基准。
3. 对照资料库文件：四月页面中 pages/flower-course.md 与 pages/spring-plan.md 不存在；flower-course-v2.md 是另一条路径，不能替代。

作答：2。

## Why the answer is unique
诱饵 1 把 flower-course-v2.md 当成 flower-course.md，两条路径字面不同且草稿页自注「尚未发布」，不能替代；诱饵 3 依赖把 10/04/2026 读成 4 月 10 日，与备注写明的 月/日/年 冲突。四月窗口内的断链唯一为 flower-course.md 与 spring-plan.md，答案唯一为 2。
