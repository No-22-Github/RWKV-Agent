## Traps
- TR-ABSENT: waitlist_notify_hours is defined in neither layer, so it has no
  effective value at all.
- TR-NEARNAME: booking-defaults.json carries cancel_notify_hours (12), a
  near-named notify-hours key whose figure is the value a conflating solver
  reports.

## Reference solution
1. Read README.md: the two config layers, the fallback, and that a key in
   neither layer has no effective value.
2. Read config/booking.json: no waitlist_notify_hours.
3. Read config/booking-defaults.json: no waitlist_notify_hours either; the file
   does carry cancel_notify_hours, which is about cancellations, not the
   waitlist. Final answer in two or three sentences per allocation v1.3 §4.1
   row 1: name both files checked, say the waitlist key has no record in either
   layer, point to the near-named cancel key without quoting its figure, and
   name the next step. Scored with output_contains_any over the key's three
   surface forms; output_excludes rules out UNKNOWN, the no-tools claim and the
   12 figure.

## Why the answer is unique
The README states the instance config overrides the defaults, that unset keys
fall through, and that a key in neither layer has no value; those two files are
the whole config surface, so waitlist_notify_hours has no effective value at
all. The decoy 12 is the defaults' cancel_notify_hours, a different key whose
figure says nothing about the waitlist; reading one key as the other is the
mistake the case is built around, so no reply that quotes a figure can be
right, and every accepted surface form names that one missing key.
