## Traps
- TR-ABSENT: ssl_min_version 在被问的范围内没有定义。
- TR-DECOY: relay-01 sets TLS1.2; relay-02 only has ssl_ciphers.

## Reference solution
Read relay-02.cfg: no ssl_min_version.

## Why the answer is unique
relay-02.cfg does not set ssl_min_version (only ssl_ciphers); TLS1.2 belongs to relay-01.
