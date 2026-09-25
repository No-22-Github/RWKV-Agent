## Traps
- TR-DECOY: trolleys/rivet.py also calls fit_canopy, so counting the whole tree rather than the
  frames and spars modules gives 5.

## Reference solution
1. Read the frames and spars modules and find the import line each carries for fit_canopy
   (call 1).
2. Count the calls: frames/assembly.py has one, frames/runner.py has two, spars/relay.py has one
   (call 2).
3. stretchers/store.py defines the helper rather than calling it, and trolleys/rivet.py is
   outside the modules the question names (call 3).

## Why the answer is unique
The frames and spars modules hold four call sites, and the definition is in the store module. A
count that sweeps the whole tree adds the trolley call and reaches 5, which is not what the
question asks for. The answer is 4.
