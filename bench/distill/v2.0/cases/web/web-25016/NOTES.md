## Traps
No traps. One search returns the deprecation notice and its first paragraph carries
the window.

## Reference solution
1. Search for the Tarnwell invoice deprecation; the only result is
   docs.tarnwell.example/deprecations/legacy-invoices.
2. Open the notice: the /v1/invoices endpoints keep accepting requests for 240 days
   from the date of the notice.

## Why the answer is unique
The notice states one window for the deprecated endpoints and one event at its end,
that every request is answered 410. It also separates sandbox access, which stays
open, so the only figure attached to the deprecated endpoints is 240 days. The date
on the notice is 11 May 2026, which fixes the window as 240 days from the notice
rather than from any other event.

## Five alternative phrasings of the task
1. tarnwell legacy invoice endpoints deprecation
2. tarnwell /v1/invoices notice window days
3. how long do tarnwell v1 invoices keep working
4. tarnwell invoice api sunset notice
5. tarnwell deprecated invoice endpoints 410
