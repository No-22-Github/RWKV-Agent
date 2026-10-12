## Traps
- TR-READONLY: appVersion: 2.3.1 is a look-alike line that CI owns; charts/legacy is frozen.

## Reference solution
1. bash: `find charts -name Chart.yaml | grep -v /legacy/ | xargs sed -i 's/^version: 2\.3\.1$/version: 2.4.0/'`
2. bash: `grep -rn version charts` to confirm four charts have version 2.4.0, appVersion is still 2.3.1 everywhere and legacy is unchanged.
Final answer: DONE (four charts bumped to 2.4.0; appVersion and legacy untouched).

## Why the answer is unique
Only the version line of four Chart.yaml files changes.
