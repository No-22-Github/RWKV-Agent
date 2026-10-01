## Traps
- TR-AMBIG: Kestrel Homes invoices sit in two files and the provisional one adds HV-233 (2110.00); picking it gives 8400.75. Turn 1 must name both candidate files and let the user pick.

## Reference solution
1. Turn 1: list the invoices directory, see the issued and provisional files, name both and ask which to use.
2. Turn 2: the user picks the issued file.
3. Read invoices/invoices-issued.csv, keep Kestrel Homes rows: 4820.00 and 1470.75.
4. Total 6290.75 and reply with the number alone.

## Why the answer is unique
 The decoy 8400.75 includes provisional HV-233, which the README says is not yet issued; a client statement is billed from the issued file, so once the user picks it the total can only be 6290.75.

## Five alternative phrasings of the task
1. What has Kestrel Homes been invoiced in total?
2. Add up the Kestrel Homes invoices, please.
3. Give me the Kestrel Homes invoice total.
4. I need the total billed to Kestrel Homes.
5. Sum the Kestrel Homes invoices for the statement.
