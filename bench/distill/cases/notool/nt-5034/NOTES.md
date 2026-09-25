## Traps
- TR-NOTOOLNEED: the manifest line and the storage table are in the workspace, and the binary ladder is a standing convention. Reading KiB as the decimal KB gives a 512,000 byte image.

## Reference solution
No steps; ref_calls is 0. Multiply 512 KiB by 1,024 bytes. The answer is 524288.

## Why the answer is unique
A KiB is 1,024 bytes, so the image is 512 x 1,024 = 524,288 bytes. 512,000 is 512 x 1,000, the decimal KB row that sits at the bottom of the same table; the manifest column is headed KiB and the binary ladder is what the release desk books, so the decimal row does not apply. The 12,288 byte difference is exactly the sort of gap that makes a flashed image fail its checksum.
