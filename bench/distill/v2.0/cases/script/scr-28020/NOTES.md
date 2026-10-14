## Traps
- CRLF leaves '\r' on each allow-list name, so no event matches.

## Reference solution
Read script, switch to splitlines(), read back.

## Why the answer is unique
Names in the allow-list are matched properly.
The fixed script prints:
lisi 2
wangwu 1
zhangsan 3
