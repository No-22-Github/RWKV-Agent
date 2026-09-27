## Traps
- TR-AMBIG: the request names The Long Gallery while hires/july-2026.csv holds two candidates, Hollybank and Stonecross. Reading it as Stonecross gives 480.5; the request was settled on Hollybank, giving 1043 (from hires/july-2026.csv). The data alone cannot say which candidate the request means, so the assistant has to ask before answering.

## Reference solution
1. Turn 1: the request names The Long Gallery but the workspace holds two candidates, Hollybank and Stonecross, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds hires/july-2026.csv and README.md.
3. read hires/july-2026.csv and take the total of the fee column for Hollybank: 1043.

## Why the answer is unique
The decoy 480.5 belongs to Stonecross; it answers a different candidate, and the request was settled on Hollybank before the count was taken.
Every row names its candidate in full, so no row counts for both, and no third reading of the file exists. The answer is 1043.

## Five alternative phrasings of the task
1. garrick manor trust long gallery hire revenue july 2026
2. room fees at hollybank and stonecross
3. july income for the two long galleries
4. long gallery hires garrick manor trust
5. july cleaning budget from room income
