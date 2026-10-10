## Traps
- TR-NEARNAME: ticket-api-sandbox is a prefix-extended twin of ticket-api and
  carries rate_limit_per_min 60; the production answer is 600. Grabbing the
  first plausible-looking 60 (or the wrong block) reports the sandbox figure.

## Reference solution
1. Read config/services.yaml (path given in the prompt).
2. Locate the ticket-api block (top-level name, no -sandbox suffix) and read
   rate_limit_per_min: 600.

## Why the answer is unique
The README states the indented lines belong to the service named directly above
them and that the sandbox is unrelated to production, so the two blocks cannot
be swapped. The prompt names the production service, whose block carries 600;
the sandbox block carries 60, and no reading of the YAML makes 60 the
production value.
