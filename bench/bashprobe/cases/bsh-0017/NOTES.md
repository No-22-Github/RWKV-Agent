pip/python are unavailable; the means are still computable. Answer cpu 54.72, mem 61.21.

Reference bash:

    awk -F, 'NR>1{c+=$2;m+=$3;n++} END{printf "%.2f %.2f\n", c/n, m/n}' data/metrics.csv

<!-- BASHPROBE-CANARY-7d41c0e9 : never enters training corpora -->
