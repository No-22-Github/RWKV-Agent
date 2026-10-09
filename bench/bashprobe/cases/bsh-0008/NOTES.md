18 renames; notes.txt untouched.

Reference bash:

    for f in photos/*.jpeg; do mv "$f" "${f%.jpeg}.jpg"; done

<!-- BASHPROBE-CANARY-7d41c0e9 : never enters training corpora -->
