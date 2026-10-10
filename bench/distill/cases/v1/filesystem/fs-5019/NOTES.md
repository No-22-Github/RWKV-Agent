## Traps
- TR-DECOY: declarations/gladys-h-0715.txt is the next morning's declaration, typed from the sheet that was filed twice, so it reads like the same document: same vessel, same quay, a weight that differs by one tenth. A solver who picks the similar-looking sheet instead of comparing the sheets reports 226 crates, which is the wrong answer. The two files that are byte for byte the same declaration are declarations/gladys-h-0714-market.txt and declarations/gladys-h-0714-office.txt, and both read 218 crates.

## Reference solution
1. list_files (1): README.md and four sheets under declarations/.
2. read_file declarations/gladys-h-0714-market.txt (2): landing declaration for the Gladys H, 218 crates, landed 2026-07-14 05:20.
3. read_file declarations/gladys-h-0714-office.txt (3): the same sheet word for word, 218 crates, so these two are the declaration filed twice.
4. read_file declarations/gladys-h-0715.txt (4): the next morning's declaration, 226 crates, which is a different sheet and not part of the pair.

## Why the answer is unique
The question asks for the sheet that is filed twice, which is settled by comparing the files with each other, not by resemblance. Exactly two sheets in the folder hold the same bytes, the market copy and the office copy of the 2026-07-14 landing, and both of them read 218 crates on their own crate line. The 0715 sheet differs from both, its landed line reads a different morning and its crate line reads 226, so it is not a copy of the pair and 226 is not the count of the doubled declaration. The Rose of Penwith sheet covers a different vessel and 90 crates. One pair, one crate figure inside it, so the answer is 218.
