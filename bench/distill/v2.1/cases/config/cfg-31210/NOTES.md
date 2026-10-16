## Traps
- TR-ABSENT: max_upload_mb 在被问的范围内没有定义。
- TR-DECOY: prod sets 200; staging.conf has no max_upload_mb.

## Reference solution
Read staging.conf: not defined.

## Why the answer is unique
staging.conf does not define max_upload_mb (only listen, workers, client_body_timeout); 200 is the prod value.
