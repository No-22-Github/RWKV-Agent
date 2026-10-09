Amounts of exactly 500 are not 'over 500'. Answer 6.

Reference bash:

    jq '[.orders[] | select(.status=="refunded" and .amount>500)] | length' orders.json

<!-- BASHPROBE-CANARY-7d41c0e9 : never enters training corpora -->
