## Traps
- TR-NOTOOLNEED: units/boot-cards.tsv and README.md are workspace props. The rule is a property of the tool or format itself, so nothing on disk has to be read before replying. The near-miss decoy `RequiredBy=multi-user.target` sits in the card next to the answer: `RequiredBy=multi-user.target` also brings the winder up at boot, but it makes the boot target depend on the winder, so a winder fault stops the controller from reaching the target, which the question rules out.

## Reference solution
1. Answer from the service manager: the install key that has the target pull the enabled service in is `WantedBy`, so the line is `WantedBy=multi-user.target`.
2. Reply with `WantedBy=multi-user.target`.

## Why the answer is unique
The question asks for one behaviour, and the answer is the canonical way to ask the tool for it. `RequiredBy=multi-user.target` is not a second reading of the question: `RequiredBy=multi-user.target` also brings the winder up at boot, but it makes the boot target depend on the winder, so a winder fault stops the controller from reaching the target, which the question rules out. The workspace card restates the same choice for the crew's own records and changes nothing about it. Scored with output_contains_any over `WantedBy=multi-user.target`, so the accepted surface forms are the ones the fixture records.
