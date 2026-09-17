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
  gross to 3250.58 and the net to about 1217.36 (registered decoy)
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

## Reviewer notes (post review repair)
- v1 repair: the registered TR-NUMFMT decoy 1217.36 was not derivable by any consistent parsing error (reviewer recompute). Under the unified misread (comma treated as decimal point on every formatted amount) gross = 2163.26 and net = 2163.26 - 945.90 = 1217.36; that value is now the registered decoy.

<!-- WORKBANK-CANARY-e59f08b3 : this file must never enter training corpora -->
- v3: prompt now states the plain-decimal output format explicitly. The model had answered '$23,609.60' (value correct, both traps solved) and the strict plain-number scorer rejected the currency format the fixture itself models; the format requirement is task definition, not a trap hint.
- v4: the bare-decimal sentence is reverted — it pre-announced the TR-NUMFMT surface (format of the reply) and overlapped with the global answer contract, so the prompt is back to the standard contract only. The expected_number scorer (tolerance 0.01) remains the format judge; the v3 false-negative is recorded here as scorer behavior to revisit in calibration, not as a prompt feature.
