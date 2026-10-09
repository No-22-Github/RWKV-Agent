Two duplicate pairs (one in a subfolder, different extensions); near_miss.bin has the same size as file_05.bin but different bytes.

Reference bash:

    find downloads -type f | xargs sha256sum | sort | awk '{print $1}' | uniq -d

<!-- BASHPROBE-CANARY-7d41c0e9 : never enters training corpora -->
