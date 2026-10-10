## Traps
- TR-FETCHFAIL: the vendor event-code appendix ranks first but its page fetch fails with a 502 provider error, so the answer has to come from the installer bulletin instead of giving up.
- TR-SNIPPETVAGUE: the appendix snippet only says codes are documented in the appendix, and the bulletin snippet names no meaning, so neither snippet can settle the question without opening the bulletin.

## Reference solution
1. web_search sunhollow sh-5k event f-07 meaning
2. web_fetch docs.sunhollowenergy.example/appendix/event-codes; the extract fails with a 502 provider error
3. web_fetch www.sunhollowenergy.example/installers/bulletins/f07; F-07 is a DC ground fault and the string insulation must be tested
4. Answer from the bulletin.

## Why the answer is unique
The installer bulletin (issued 2026-07-30) states F-07 is a DC ground fault and requires the string insulation to be tested before re-energising; both judged phrases come from that page. The ranked appendix page cannot answer: its snippet is generic and its fetch fails with a 502, so it offers no competing value and the bulletin is the only readable source. The answer admits no second reading.

## Five alternative phrasings of the task
1. sunhollow sh-5k event f-07 meaning
2. sunhollow inverter f-07 what to do
3. sunhollow f-07 installer bulletin
4. sunhollow string inverter event codes f-07
5. sunhollow sh-5k latched out f-07
