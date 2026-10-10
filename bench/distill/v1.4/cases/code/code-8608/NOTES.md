## Traps
- TR-DECOY: rails-html-sanitizer (1.6.0) is listed right below rails in the lock.

## Reference solution
1. Read the basis Gemfile.lock: the new value is 7.1.3.
2. Read Gemfile: line 2, `gem 'rails', '7.0.8'`, is the one to change.
3. replace_lines line 2 with `gem 'rails', '7.1.3'`; the rest of the line stays.
4. Read Gemfile back to confirm.
Final answer example: The Gemfile now asks for rails 7.1.3, matching Gemfile.lock. / DONE
Criteria: exact target file content; output contains DONE.

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.
