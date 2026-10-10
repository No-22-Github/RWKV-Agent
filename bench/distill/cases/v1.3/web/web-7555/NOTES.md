## Traps
- TR-WEBSTALE: 排第一的是官方 2026 页（成人 9.50 镑）；排第二的游记是
  2023 年的，成人 8 镑，是三年前的旧价（decoy 8）。
- TR-DECOY: 同一官方页上还有年票 28 镑、儿童 4 镑，年票 28 是同页相邻
  干扰值（decoy 28）。

## Reference solution
1. web_search thornreach wharf admission (1)
2. web_fetch www.thornreachwharf.example/visit (2)
3. Read the 2026 admission line and answer 9.5 (3)

## Why the answer is unique
The museum's own 2026 admission line prices adults at 9.50 pounds; 4 pounds
is the child price and 28 pounds the annual pass, both different products on
the same page. The visitor post's 8 pounds describes a 2023 visit and even
tells readers to check current prices, so 9.5 is the only supportable adult
admission for today.

## 正确答案
9.5

## Five alternative phrasings
1. thornreach wharf adult admission price
2. thornreach wharf museum entry fee 2026
3. how much is thornreach wharf entry
4. thornreach wharf plan your visit prices
5. thornreach wharf tickets adults
