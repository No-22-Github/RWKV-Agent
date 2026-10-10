## Traps
- none: flat single-file config, the asked key is defined once. Base L0 of the
  family.

## Reference solution
1. Read config/press-line.yaml (path given in the prompt): print_mode is duplex.

## Why the answer is unique
The README says the YAML is the effective config and panel choices do not count,
so there is exactly one place to look. print_mode is defined once and the two
accepted surface forms (duplex / 双面) name the same single value; simplex is
not the configured mode and a reply carrying simplex without duplex fails the
contains-any check.
