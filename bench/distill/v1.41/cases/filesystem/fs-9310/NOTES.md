## Traps
- TR-READONLY: 001_init.sql has already run everywhere and must not change (db/README.md).
- TR-DECOY: orders_archive, idx_orders_status, big_orders and order_items contain 'order(s)' but are other objects;.

## Reference solution
1. bash: `ls db/migrations/*.sql | grep -v 001_init | xargs sed -i 's/\borders\b/sales_orders/g'`
2. bash: `grep -rn 'orders' db/migrations` to confirm the target files changed and the protected ones did not.
Final answer: DONE (002 to 005 use sales_orders as a whole word; 001_init.sql and the orders_archive, order_items and index names are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (4 files change).

## Five alternative phrasings of the task
1. 把迁移文件里的表名 orders 统一换成 sales_orders，已经执行过的 001 不要改。
2. db/migrations 下除了 001_init.sql，所有 SQL 里作为表名的 orders 改为 sales_orders，别误伤 orders_archive 等。
3. orders 表重命名为 sales_orders，同步更新后面的迁移脚本，README 里说不动的保持原样。
4. 重命名表 orders → sales_orders（只改整词），迁移 002 到 005 都要更新，改完回复 DONE。
5. Rename the table orders to sales_orders in the not-yet-applied migrations only, reply DONE.
