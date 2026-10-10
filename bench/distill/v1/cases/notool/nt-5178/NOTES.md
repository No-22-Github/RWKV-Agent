## Traps
- TR-NOTOOLNEED: transfer/mirror-option-cards.tsv and README.md are props. What an option does to the receiving side is a property of the transfer tool, so no file has to be read. The near-miss decoy `--remove-source-files` deletes the files that were transferred on the sending side, so the office copy loses plans while the laptop keeps its extras, the opposite of what is asked.

## Reference solution
1. Answer from the tool: the option that removes files on the receiving side that the source does not have is `--delete`.
2. Reply with `--delete`.

## Why the answer is unique
The question asks for the receiving side to lose the files the source no longer has, and `--delete` is the option that removes destination files that are absent from the source. `--remove-source-files` cannot be a reading of the question: it acts on the sending side, deleting the plans that were just copied, and leaves every extra file on the laptop in place.
