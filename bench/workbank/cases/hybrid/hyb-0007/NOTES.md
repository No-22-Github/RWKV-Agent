## Traps
- TR-SUPERSEDE: the 6.0 acceleration post (published 2026-03-12) ranks first in search and carries the eye-catching major number, but it describes a preview series. The releases page (published 2026-09-02) is the later document and marks 5.x as the stable series, with 5.3.1 (2026-08-26) as its newest stable entry. Setting the pin to the preview's 6.0.0 is the decoy; the supported stable release is 5.3.1.

## Reference solution
1. web_search saltmarsh releases (1)
2. web_fetch the releases page; it marks 5.x stable and 6.x preview, and its newest stable entry is 5.3.1 (2026-08-26) (2)
3. read_file tools/requirements.txt (3)
4. write_file tools/requirements.txt with the saltmarsh pin set to 5.3.1 and the other two pins untouched (4); reply DONE

ref_calls = 4 (fetching the preview post as well is optional; the releases page alone settles the question).

## Why the answer is unique
The prompt asks for the supported stable version. Only the releases page classifies its entries, and it marks 5.x as the current stable series and 6.x as a preview that is not published for production; among the stable entries, 5.3.1 carries the later date. The contains-checks on all three pins plus unchanged checks on README.md and tools/dispatch.py pin down the edit. README.md only says the desk keeps the list in step with the vendor's published releases; it is the releases page, not the README, that separates the stable series from the preview, and the prompt asking for the supported stable version is what makes 6.0.0 out of scope.

## Five alternative phrasings of the task
1. saltmarsh releases
2. saltmarsh stable version
3. saltmarsh python queue library
4. saltmarsh version history
5. saltmarsh supported release

<!-- WORKBANK-CANARY-c9d40f16 : this file must never enter training corpora -->
