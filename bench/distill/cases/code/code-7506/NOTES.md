## Traps
- TR-DECOY: src/warehouse_api.py 里并存 sanitize_sku_legacy，名字相近，粗读会把 legacy 当成被调用的实现。 A careless pass reports `sanitize_sku_legacy`.

## Reference solution
1. Read src/warehouse_api.py and see what post_inbound calls.
2. Follow the import to the defining module.
3. Read src/sku_text.py and confirm the canonical definition; note the legacy variant is a separate function.

## Why the answer is unique
post_inbound calls the imported name sanitize_sku, and the import points at src/sku_text.py; sanitize_sku_legacy is a distinct function that nothing in post_inbound references and its docstring limits it to replay scripts. The canonical definition is therefore the one in sku_text.py.
