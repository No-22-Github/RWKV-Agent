## Traps
- ruby is not installed, so `ruby tools/buyers.rb` exits 127; the script has to be reproduced by hand.
- TR-DEFN: counting paid rows gives 148; the script counts distinct customers.
- TR-DECOY: state paid-pending is not paid; a prefix match gives 82 customers.

## Reference solution
1. bash: `ruby tools/buyers.rb` -> exit 127.
2. read_file tools/buyers.rb: distinct customers over rows whose state is exactly paid.
3. bash: `cat data/*.csv | awk -F, '$3=="paid" {print $2}' | sort -u | wc -l`
Final answer: buyers.rb prints "distinct paying customers: 73" (ruby is not available; recomputed with awk and sort -u).

## Why the answer is unique
The script's key is the customer id and its filter is the exact state paid.

## Alternative phrasings
1. Run tools/buyers.rb and tell me how many distinct paying customers it reports.
2. What number does tools/buyers.rb print for distinct paying customers?
3. Execute the buyers script and give me the customer count it outputs.
4. tools/buyers.rb counts unique customers with a paid order: what is the result?
5. Please run buyers.rb and report its distinct paying customer figure.
