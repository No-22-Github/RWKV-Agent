## Traps
- TR-AMBIG: the first request asks what the order "comes to" while every line
  carries a trade price and a retail price. Priced from the trade column the
  order is 1225.10; priced from the retail column it is 1878.90. The request and
  the README both leave the basis open, so the assistant has to ask which column
  the customer is billed from.

## Reference solution
1. Turn 1: the order form holds two price columns and the request does not say
   which applies, so the assistant asks and calls no tool.
2. list_files: the workspace holds orders/hallam-2026-09.csv and README.md.
3. Turn 2 fixes the trade prices. read_file the order and multiply each line:
   120 x 3.45 + 80 x 3.80 + 250 x 1.15 + 180 x 1.22 = 414.00 + 304.00 + 287.50 +
   219.60 = 1225.10.

## Why the answer is unique
With the basis fixed, each line contributes quantity times one stated price and
nothing else: no line is discounted, repeated or left blank, and the README says
the quantity column is what the customer asked for. The decoy 1878.90 is the
same order priced from the retail column, which is a real column of the same
file but not the basis the customer was settled on. The trade-priced total is
1225.10.

## Five alternative phrasings of the task
1. aldermere nurseries hallam garden centre september order total
2. hallam order priced at trade rates
3. nursery order form with trade and retail price columns
4. beech hornbeam dog rose order value for hallam
5. aldermere nurseries september order form line totals
