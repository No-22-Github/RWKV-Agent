## Traps
TR-TRUNC, TR-SUPERSEDE

## Reference solution
 一次 web_fetch 同时取 2 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
write_file 写入 pylume-compare.md
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
13734
(fixture: pylume.example/docs/3.4/install=4597, pylume.example/docs/4.0/install=4737)


## Five alternative phrasings of the task
1. 我们服务器上跑的是 Pylume 3.4，在看要不要升级到 4.0。对比一下两版安装文档：https://pylume.example/docs/3.4/install 和 https://pylume.example/docs/4.0/install 。把 Python 版本、CUDA 要求、4.0 什么时候转正、3.4 维护到什么时候写进 pylume-compare.md。
2. 麻烦帮我：我们服务器上跑的是 Pylume 3.4，在看要不要升级到 4.0。对比一下两版安装文档：https://pylume.example/docs/3.4/install 和 https://pylume.example/docs/4.0/install 。把 Python 版本、CUDA 要求、4.0 什么时候转正、3.4 维护到什么时候写进 pylume-compare.md。
3. 我们服务器上跑的是 Pylume 3.4，在看要不要升级到 4.0。对比一下两版安装文档：https://pylume.example/docs/3.4/install 和 https://pylume.example/docs/4.0/install 。把 Python 版本、CUDA 要求、4.0 什么时候转正、3.4 维护到什么时候写进 pylume-compare.md。（用中文回答）
4. 想请你看看：我们服务器上跑的是 Pylume 3.4，在看要不要升级到 4.0。对比一下两版安装文档：https://pylume.example/docs/3.4/install 和 https://pylume.example/docs/4.0/install 。把 Python 版本、CUDA 要求、4.0 什么时候转正、3.4 维护到什么时候写进 pylume-compare.md。
5. 再确认一下：我们服务器上跑的是 Pylume 3.4，在看要不要升级到 4.0。对比一下两版安装文档：https://pylume.example/docs/3.4/install 和 https://pylume.example/docs/4.0/install 。把 Python 版本、CUDA 要求、4.0 什么时候转正、3.4 维护到什么时候写进 pylume-compare.md。
