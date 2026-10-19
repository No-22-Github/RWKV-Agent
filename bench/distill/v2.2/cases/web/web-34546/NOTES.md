## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
 一次 web_fetch 同时取 3 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
15451
(fixture: netwave-router.example/support/ax6-firmware=3873, netwave-router.example/notice/security-1008=3785, routerclub.example/t/ax6-2-1-8-feedback=3443)


## Five alternative phrasings of the task
1. 我的 NetWave AX6 路由器要不要升级？看看官方支持页 https://netwave-router.example/support/ax6-firmware 、安全公告 https://netwave-router.example/notice/security-1008 和论坛反馈 https://routerclub.example/t/ax6-2-1-8-feedback ，告诉我最新版本、哪些版本有漏洞、升级后有什么问题以及怎么处理。
2. 麻烦帮我：我的 NetWave AX6 路由器要不要升级？看看官方支持页 https://netwave-router.example/support/ax6-firmware 、安全公告 https://netwave-router.example/notice/security-1008 和论坛反馈 https://routerclub.example/t/ax6-2-1-8-feedback ，告诉我最新版本、哪些版本有漏洞、升级后有什么问题以及怎么处理。
3. 我的 NetWave AX6 路由器要不要升级？看看官方支持页 https://netwave-router.example/support/ax6-firmware 、安全公告 https://netwave-router.example/notice/security-1008 和论坛反馈 https://routerclub.example/t/ax6-2-1-8-feedback ，告诉我最新版本、哪些版本有漏洞、升级后有什么问题以及怎么处理。（用中文回答）
4. 想请你看看：我的 NetWave AX6 路由器要不要升级？看看官方支持页 https://netwave-router.example/support/ax6-firmware 、安全公告 https://netwave-router.example/notice/security-1008 和论坛反馈 https://routerclub.example/t/ax6-2-1-8-feedback ，告诉我最新版本、哪些版本有漏洞、升级后有什么问题以及怎么处理。
5. 再确认一下：我的 NetWave AX6 路由器要不要升级？看看官方支持页 https://netwave-router.example/support/ax6-firmware 、安全公告 https://netwave-router.example/notice/security-1008 和论坛反馈 https://routerclub.example/t/ax6-2-1-8-feedback ，告诉我最新版本、哪些版本有漏洞、升级后有什么问题以及怎么处理。
