## Traps
- TR-PRECEDENCE: base carries `request_timeout_s` 12 and booking re-sets it to 20 one step up the chain, so tracking inherits 20. A solver that reads the base block and stops, or that resolves only one step of the chain, reports 12.

## Reference solution
1. Read README.md: a service block applies its own keys on top of the block named in `inherits`, and chains can run more than one step deep.
2. Read config/services.json: tracking inherits booking, booking inherits base and sets `request_timeout_s` 20, and tracking sets no timeout of its own. The effective value is 20.

## Why the answer is unique
The README fixes how inheritance resolves: a service keeps the inherited value for any key it does not set, so booking's 20 is what tracking enforces. The decoy 12 is the base value, which booking replaced, so reading it through the chain is the mistake the case is built around. The answer is 20.
