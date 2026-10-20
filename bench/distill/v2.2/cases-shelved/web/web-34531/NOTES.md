## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
 一次 web_fetch 同时取 2 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
13788
(fixture: lantu-charts.example/docs/changelog=4988, devnotes-liu.example/posts/lantu-charts-review=4650)


## Five alternative phrasings of the task
1. 岚图表这个库，我搜到官方更新日志 https://lantu-charts.example/docs/changelog 和一篇个人博客 https://devnotes-liu.example/posts/lantu-charts-review ，两边说法不太一致。帮我对比一下：最新版本是多少、要什么 Node 版本、许可证是什么，哪份资料更新更可信？
2. 麻烦帮我：岚图表这个库，我搜到官方更新日志 https://lantu-charts.example/docs/changelog 和一篇个人博客 https://devnotes-liu.example/posts/lantu-charts-review ，两边说法不太一致。帮我对比一下：最新版本是多少、要什么 Node 版本、许可证是什么，哪份资料更新更可信？
3. 岚图表这个库，我搜到官方更新日志 https://lantu-charts.example/docs/changelog 和一篇个人博客 https://devnotes-liu.example/posts/lantu-charts-review ，两边说法不太一致。帮我对比一下：最新版本是多少、要什么 Node 版本、许可证是什么，哪份资料更新更可信？（用中文回答）
4. 想请你看看：岚图表这个库，我搜到官方更新日志 https://lantu-charts.example/docs/changelog 和一篇个人博客 https://devnotes-liu.example/posts/lantu-charts-review ，两边说法不太一致。帮我对比一下：最新版本是多少、要什么 Node 版本、许可证是什么，哪份资料更新更可信？
5. 再确认一下：岚图表这个库，我搜到官方更新日志 https://lantu-charts.example/docs/changelog 和一篇个人博客 https://devnotes-liu.example/posts/lantu-charts-review ，两边说法不太一致。帮我对比一下：最新版本是多少、要什么 Node 版本、许可证是什么，哪份资料更新更可信？
