## Traps
None. Six consignments, one weight column, and the heaviest row is the only row
carrying that figure.

## Reference solution
1. list_files: the workspace holds weighbridge/consignment-book.csv and README.md.
2. read_file weighbridge/consignment-book.csv: the tonnes column holds 38, 57, 44, 51,
   29 and 62, so the heaviest consignment TH-4476 weighed 62 tonnes.

## Why the answer is unique
The book carries one net weight per consignment and the README says the tonnes column
is the net figure, so no row has to be adjusted before it is compared. 62 appears once
in the column and no other consignment comes near it (the next heaviest is 57), so the
heaviest consignment is unambiguous and its weight is 62.

## Five alternative phrasings of the task
1. thurlstone timber september weighbridge book
2. heaviest consignment at thurlstone timber
3. thurlstone timber net tonnes per consignment
4. thurlstone sawmill september return weights
5. thurlstone timber consignment weights
