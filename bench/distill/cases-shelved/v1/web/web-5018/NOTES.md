## Traps
- TR-EARLYHIT: the first result is the changelog entry for the newest release and its
  snippet gives the worker count outright, so one search is enough and the case caps
  web_search at 1. skerriford.example/guides/server-install is the decoy: it pins 18,
  but only for a shared server and for the older 5.x line.

## Reference solution
1. Search once for the Skerriford exporter release: the first result is the 6.2 changelog
   entry with the shipped worker count in its snippet, and the install guide is listed
   with it.
2. Open skerriford.example/changelog/2026-08-19: the shipped worker count is 32, raised
   from 24, and a fresh installation takes the shipped figure.

## Why the answer is unique
The changelog speaks for the newest release and says the installer writes no worker count
into the configuration, so a fresh installation takes 32. The install guide is written
for the 5.x line, and its 18 applies to a shared server, which the question does not
describe. 24 is the figure 6.2 replaced, named on the same page as the old value.

## Five alternative phrasings of the task
1. skerriford exporter newest release worker count
2. skerriford exporter 6.2 shipped defaults
3. how many workers does a skerriford exporter run use
4. skerriford exporter changelog worker count
5. skerriford exporter fresh installation defaults
