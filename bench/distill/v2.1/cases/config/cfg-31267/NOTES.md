## Traps
- TR-ABSENT: 问题的后半部分（tls_cert_path）查不到。
- TR-DECOY: tls: false explains the missing path.

## Reference solution
port 9273 is present; tls is false and there's no tls_cert_path.

## Why the answer is unique
Read exporter.yaml: port 9273; no tls_cert_path (tls is off).
