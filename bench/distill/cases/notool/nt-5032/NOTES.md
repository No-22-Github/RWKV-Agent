## Traps
- TR-NOTOOLNEED: the lease table and the capacity table are in the workspace, and the binary ladder is a standing convention. Reading the leases as decimal TB gives a 3,500 GiB quota.

## Reference solution
No steps; ref_calls is 0. Add the two leases to 3.5 TiB and multiply by 1,024. The answer is 3584.

## Why the answer is unique
The leases are booked in TiB, the binary unit, and one TiB is 1,024 GiB, so 3.5 x 1,024 = 3,584 GiB. 3,500 is 3.5 x 1,000, the decimal TB row that sits below the TiB row in the same table; the lease column is headed TiB and the tool quota is in GiB, so only the 1,024 row applies. Provisioning 3,584 GiB honours the lease, while 3,500 would leave the tenants short of what the rack was sold as.
