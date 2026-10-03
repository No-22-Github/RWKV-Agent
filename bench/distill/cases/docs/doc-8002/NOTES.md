## Traps
- TR-ABSENT: oncall/2026-Q4.md has no row for billing. services/catalogue.md says billing moved to the Revenue Platform pager tool on 2026-09-01 and is not in the shared rota.
- TR-DECOY: the rota does have a billing-legacy row, and its Oct 13 entry is Priya Venkataraman. billing-legacy was decommissioned on 2026-08-15, so naming Priya Venkataraman is the decoy answer.

## Reference solution
1. List the workspace: oncall/2026-Q4.md, oncall/README.md, services/catalogue.md.
2. Read oncall/2026-Q4.md: no billing row, only billing-legacy.
3. Read services/catalogue.md: billing is owned by Revenue Platform and paged from their own tool since 2026-09-01; billing-legacy is decommissioned.
Final answer (2-4 sentences): the shared Q4 rota has no billing row, so it cannot say who is on call for billing the week of Oct 13; the billing-legacy row in it belongs to a service decommissioned in August. Billing moved to the Revenue Platform pager tool on Sep 1, so the person to check with is Revenue Platform (or their pager schedule). Criteria: mentions billing and Revenue Platform; must not name the billing-legacy engineers.

## Why the answer is unique
billing-legacy is a different, decommissioned service; the catalogue keeps its rotation only until the rota is regenerated, so its engineers are not on call for the live billing service. The catalogue states billing left the shared rota, and nothing else in the workspace lists a billing pager rotation, so the only correct reply is that the rota does not cover it and Revenue Platform does.
