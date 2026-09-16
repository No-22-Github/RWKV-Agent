## Traps
- TR-SIGN: refunds_april.csv stores each refund as a positive figure; the
  README states a refund reduces the revenue recognized on the referenced
  order. A model that reads the positive refunds as money flowing toward
  us and adds them gets 25501.40 (registered decoy) instead of 23609.60.
- TR-NUMFMT: amounts are written like "$1,129.90" (dollar mark, thousands
  comma, quoted field), so direct aggregation over the raw column errors
  out and the model must re-parse the text by hand. Reading the comma as
  a decimal marker - "$12,036.40" taken as 12.0364, "$1,129.90" as
  1.1299, and so on for every thousands-separated amount - collapses the
  gross to 3250.58 and the net to about 2304.68 (registered decoy)
  instead of 23609.60.

## Reference solution
1. read_file README.md - refunds are stored as positive figures and
   reduce revenue on the referenced order (1)
2. read_file orders_april.csv - ten orders; stripping "$" and thousands
   commas gives a gross of 24555.50 (2)
3. read_file refunds_april.csv - three refunds, total 945.90 (3)
4. calculator - 24555.50 - 945.90 = 23609.60 (4)

## Why the answer is unique
The README pins the direction of the refund amounts, every refund
references an order present in the April register, and no other
adjustment source exists in the workspace. Once the "$" mark and the
thousands commas are stripped the arithmetic is a plain sum minus a
plain sum, and all ten order rows are distinct April orders.
