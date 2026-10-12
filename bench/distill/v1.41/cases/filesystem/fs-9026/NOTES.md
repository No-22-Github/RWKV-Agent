## Traps
- TR-READONLY: photos/raw/*.jpeg must keep their names (photos/README.txt); contact-sheet.jpeg.txt is a text file whose name merely contains .jpeg.

## Reference solution
1. bash: `for f in $(find photos -name '*.jpeg' | grep -v /raw/); do mv "$f" "${f%.jpeg}.jpg"; done`
2. bash: `find photos -name '*.jp*g'` to confirm the 10 files are now .jpg and photos/raw still lists three .jpeg.
Final answer: DONE, 10 .jpeg files renamed to .jpg; raw originals untouched.

## Why the answer is unique
Rename is by extension only, outside photos/raw; contents do not change.
