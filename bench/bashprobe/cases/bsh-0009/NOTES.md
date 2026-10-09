5 .tmp files at three depths under build/; src/scratch.tmp is outside scope.

Reference bash:

    find build -name '*.tmp' | xargs rm

<!-- BASHPROBE-CANARY-7d41c0e9 : never enters training corpora -->
