## Traps
- TR-MULTISRC: the core diameter is nowhere in logs/labeller.log. The journal names the reels and the jams, and the diameters are only in notes/reel-intake.md; the print offset of the first jam (27) is the most conspicuous number in the journal and is the wrong value.
- TR-DECOY: three reels were loaded during the two days the journal covers, so the reel of the previous load looks like the one that was running. The reel loaded ahead of the first jam is RL-8177; the load before it, RL-8144, has a core of 40 and is the value a reader gets by taking the wrong LOAD line.

## Reference solution
1. List the workspace: README.md, logs/labeller.log and notes/reel-intake.md.
2. Read README.md: a LOAD line records a reel being spliced in, a JAM line records the web jamming, and the reel in the applicator when the jams began is the one to trace to the goods-in book.
3. Read logs/labeller.log. The first jam is at 07:52:36 on 17 September 2026 and the last load ahead of it is `2026-09-17T07:19:04Z LOAD reel=RL-8177`, so RL-8177 was the reel in the applicator.
4. Read notes/reel-intake.md. RL-8177's core is 152 mm, so the spindle was set for that diameter.

## Why the answer is unique
README.md says a LOAD line is written when a reel is spliced in and the jams began on 17 September 2026, so the reel in the applicator when they began is the one from the last LOAD line ahead of the first JAM line, which is RL-8177; the reels loaded after it came later and the earlier loads were off the machine by then. The diameter itself is only in the goods-in book, where RL-8177's row gives a core of 152 mm. The decoy 27 is the print offset the first jam line records, a distance on the web rather than a reel dimension, and 40 is the core of the previous reel, RL-8144, which is what a reader takes by choosing the wrong LOAD line. With the reel identified and looked up, the answer is 152.

## Fixture notes
The journal spans 16 and 17 September 2026 and the goods-in book lists every reel the journal names, so the two agree. The offsets on the jam lines are millimetres of print position like the core values, which is what makes them a plausible substitute, and the core values in the table are ordinary stock sizes rather than numbers chosen to stand out.
