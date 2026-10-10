## Traps
- TR-DECOY: notes/note-a.txt and notes/note-b.txt hold the same note, including the weight 186 kg, so a solver who opens one of the two and stops reports 186, the figure the correction replaced. The re-typed copy is notes/note-c.txt and it carries 198 kg.

## Reference solution
1. list_files (1): README.md and three notes under notes/.
2. read_file notes/note-a.txt (2): delivery note 4471, consignment weight 186 kg.
3. read_file notes/note-b.txt (3): the same note, byte for byte, weight 186 kg.
4. read_file notes/note-c.txt (4): the only copy that differs, weight 198 kg, so the corrected weight is 198.

## Why the answer is unique
The three notes share one delivery note number, 4471, and two of them are byte-identical, which is the pair the question describes as saved twice. That leaves exactly one note that is not part of the pair, and its weight line reads 198 kg, so it is the re-typed copy and 198 is the corrected weight. The 186 kg figure belongs to the pair and is not a second reading of the question: the question asks for the re-typed copy, and there is exactly one such file.
