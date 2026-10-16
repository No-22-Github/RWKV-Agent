## Traps
- TR-ABSENT: cache_ttl 在被问的范围内没有定义。
- TR-DECOY: rules.yaml lists /static/*, /api/search, /api/cart only; no product-detail rule.

## Reference solution
Read rules.yaml: no rule for product detail.

## Why the answer is unique
rules.yaml has no rule for the product-detail endpoint (only /static/*, /api/search, /api/cart), so no cache_ttl applies/is defined for it.
