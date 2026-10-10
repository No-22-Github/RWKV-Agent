## Traps
- TR-AMBIG: invoices are raised per tenant but the request never says which tenant; summing every overage line gives 142.35, which bills all three tenants on one invoice.

## Reference solution
1. Turn 1: the tenant is a required parameter only the user holds; ask whose invoice this is (no tool calls).
2. Turn 2: the user names meridian-health.
3. Read usage/api-usage.csv, keep meridian-health rows: 42.60, 18.75, 55.10, 9.40.
4. Total 125.85 and reply with the number alone.

## Why the answer is unique
 The decoy 142.35 folds in corvid-retail's 12.35 and 4.15; once the invoice is scoped to meridian-health those lines belong to other invoices, so 125.85 is the only reading. Turn 1 is judged only on surfacing the missing tenant.

## Five alternative phrasings of the task
1. Whose overage am I totalling for August?
2. Add up the August overage fees for the invoice.
3. What overage do we bill this invoice run?
4. Give me the overage total for the August run.
5. Total the usage overage fees to invoice.
