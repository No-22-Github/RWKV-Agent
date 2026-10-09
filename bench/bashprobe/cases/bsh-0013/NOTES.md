3000 lines (~200KB); all fatal lines sit after line 1400, beyond read_file's 64KB and bash's 8KB output cap. 'recovered from fatal' info lines are decoys. Answer 7.

Reference bash:

    grep -c 'level=fatal' big.log

<!-- BASHPROBE-CANARY-7d41c0e9 : never enters training corpora -->
