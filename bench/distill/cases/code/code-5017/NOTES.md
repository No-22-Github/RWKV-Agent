## Traps
- TR-DECOY: line/store.py holds the definition of start_batch, and the definition line reads like a call if the reader counts every line of the shape name( without dropping the module that defines it: that count is 4 instead of 3.

## Reference solution
1. Read intake/loader.py: one call to start_batch inside load(), and the import that binds the name (call 1).
2. Read line/relay.py: one call inside relay() (call 2).
3. Read line/registry.py: one call inside register(); the name in the comment is not a call (call 3).
4. Read line/store.py: it defines start_batch and calls nothing, so the three real call sites are load(), relay() and register(). The answer is 3.

## Why the answer is unique
The decoy count 4 comes from taking the def line in line/store.py for a call site: a definition binds a name for others to call, it does not call anything itself, and the same module starts with the store's own assignments. Every other mention of the name in the workspace is an import line or prose in a comment, so counting real calls gives 3.
