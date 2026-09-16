## Traps
- TR-DIRMAP: the desk sheet's first column is "We sell USD" (0.9300); the column guide in the page body assigns "We buy USD" (0.9165) to converting dollar receipts into euros. Quoting the first column gives 10700.00 x 0.9300 = 9951.00 (decoy).

## Reference solution
1. web_search cascade trust desk rates (1)
2. web_fetch the desk-rates page; the column guide maps "dollar receipts are converted into euros" to "We buy USD" = 0.9165 (2)
3. read_file orders.csv; amount_usd sums to 10700.00 (3)
4. calculator 10700.00 x 0.9165 = 9806.55; answer 9806.55 (4)

## Why the answer is unique
One rate sheet (effective 11 September 2026) quotes a single pair, and the page's column guide assigns exactly one rate to converting USD receipts into EUR; every orders.csv row is an August order. The product is exact to the cent, so no rounding judgement is involved.

## Five alternative phrasings of the task
1. cascade trust fx desk rates
2. cascade trust usd eur rate today
3. cascade trust foreign exchange quotations
4. cascade trust desk rate for dollars
5. cascade trust currency rates september

<!-- WORKBANK-CANARY-a3f85d02 : this file must never enter training corpora -->
