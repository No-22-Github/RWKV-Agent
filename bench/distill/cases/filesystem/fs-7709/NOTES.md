## Traps
- TR-DECOY: stock/prototype-log.csv 里立牌草稿 standee-mashiro-raw.psd 有 715 MB。扫两份登记表找最大值会报 715；README 写明草稿是未采用的备查文件、盘点只看上架源文件，最大的是亚克力立牌的 386 MB。

## Reference solution
1. 列出 stock/：goods-log.csv 与 prototype-log.csv 两份登记。
2. 读 README.md：只有 goods-log.csv 的行算上架源文件，草稿不参与盘点。
3. 读 goods-log.csv：大小列最大 386，对应亚克力立牌；prototype-log.csv 是未采用草稿的备查登记。

## Why the answer is unique
诱饵 715 是草稿文件。README 规定草稿不参与盘点、只看上架源文件，所以任何草稿行都不能成为答案；上架源文件的大小列峰值是 386（亚克力立牌），高于 298 与 214。草稿登记的用途由 README 里「未采用的草稿，另存备查」一句说明。口径规则加大小列共同固定三个事实，没有第二种读法。
