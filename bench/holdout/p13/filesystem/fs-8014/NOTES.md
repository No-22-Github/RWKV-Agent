## Traps
- TR-DECOY: north-wing-0908.txt 与 north-wing-0908-v2.txt 全文只差一个数字（机柜 N-03 温度 24.6 与 24.8），目测极像重复，但逐字节不同，不构成一对。真正的重复对是 east-wing-0901-a/b（上传重试写了两份）与 west-wing-0902-a/b，共 2 对；目测口径会答 3。

## Reference solution
1. 列出工作区：5 个（实际 7 份）巡检 txt。
2. 逐对比较内容：east-wing-0901-a == east-wing-0901-b；west-wing-0902-a == west-wing-0902-b；north-wing-0908 与 -v2 有且仅有一行不同。
3. 完全相同的重复文件共 2 对。

## Why the answer is unique
「内容完全相同」按逐字节比较，两对孪生文件的每个字符都一致；north-wing 那对的差异落在单独一行的温度数字上，不属于「完全相同」。2 对是唯一与逐字节口径一致的结果。答案唯一为 2。
