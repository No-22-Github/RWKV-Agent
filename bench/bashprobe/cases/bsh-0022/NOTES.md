Sanity baseline: any read path works; bash is not needed. Use it to see whether bash crowds out read_file on trivial reads (diagnostic, not scored).

Reference bash:

    head -1 README.md

<!-- BASHPROBE-CANARY-7d41c0e9 : never enters training corpora -->
