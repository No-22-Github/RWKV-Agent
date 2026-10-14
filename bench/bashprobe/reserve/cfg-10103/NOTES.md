## Traps
- TR-READONLY: 工程/实验/ does not follow the upgrade.
- 4 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find 工程 -name pyproject.toml -not -path '*/实验/*' | xargs sed -i 's/^requires-python = ">=3.9"$/requires-python = ">=3.11"/'`
2. bash: `find 工程 -name pyproject.toml -not -path '*/实验/*' | xargs sed -i 's/^target-version = "py39"$/target-version = "py311"/'`
3. bash: `grep -rn -e requires-python -e target-version 工程`
Final answer: 四个项目的 requires-python 已是 >=3.11、ruff target-version 已是 py311，实验项目没动，grep 检查过。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
