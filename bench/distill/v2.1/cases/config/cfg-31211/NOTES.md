## Traps
- TR-ABSENT: posts_per_page 在被问的范围内没有定义。
- TR-DECOY: CHANGELOG 暗示在 app.cfg 里，但 app.cfg 里实际没有这一项，nginx.conf 的注释也没给数值。

## Reference solution
读 app.cfg：没有 posts_per_page；nginx.conf 注释没有数值；CHANGELOG 只说调整过。

## Why the answer is unique
app.cfg 里没有 posts_per_page（只有 site_name、max_title_len、spam_filter），nginx.conf 只有一句注释，所以查不到具体数值；日志提到调整过但没写数。
