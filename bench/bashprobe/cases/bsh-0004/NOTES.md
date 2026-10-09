420 rows, 3 months x 4 regions. Answer 16954.04.

Reference bash:

    awk -F, '$3=="华东" && $2 ~ /^2026-08/ {s+=$4} END{printf "%.2f\n", s}' sales.csv

<!-- BASHPROBE-CANARY-7d41c0e9 : never enters training corpora -->
