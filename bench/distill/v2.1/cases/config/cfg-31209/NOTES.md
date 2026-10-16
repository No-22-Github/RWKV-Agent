## Traps
- TR-ABSENT: JWT_EXPIRE_MINUTES 在被问的范围内没有定义。
- TR-DECOY: development 里 JWT_EXPIRE_MINUTES=720，production 没有。

## Reference solution
读 .env.production：没有该项。

## Why the answer is unique
.env.production 里没有 JWT_EXPIRE_MINUTES（只有 JWT_SECRET_REF），720 属于开发环境。
