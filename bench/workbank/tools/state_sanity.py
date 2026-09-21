#!/usr/bin/env python3
"""Magnitude gate for uploaded RWKV time-states (g1k 7B layout: blocks.N.att.time_state).

A state that was tuned into a workable regime keeps a small per-tensor RMS; a run
whose learning rate or step scale is off blows the state up and the model degrades
(unreadable continuations, single-action attractors, repetition) even though the
training loss may fall. This tool reads the tensors straight out of the torch
archive — no torch, no model load — and reports per-tensor RMS/max plus NaN/Inf,
gating on an absolute RMS ceiling and, optionally, against a reference file.

Usage:
  state_sanity.py <state.pth> [more.pth ...] [--max-rms 2.0] [--reference <healthy.pth>]
Exit code is 1 when a gated state fails, so a training loop can stop before eval.
"""
import argparse
import math
import struct
import sys
import zipfile
from pathlib import Path

REFERENCE_NOTE = """Calibration on g1k 7B bf16 time-states (2026-09-20/21, per-tensor median RMS / max|v|):

  RMS 0.0011 / 0.003   ws700 corpus, lr 1e-5   coherent; canary readable; 1/40 workbank
  RMS 0.84   / 3.6     37-row run step 18      degenerate: no tool call at all, canary loops
  RMS 1.06   / 10.3    37-row run step 108     partially coherent; canary garbled; 0/40
  RMS 3.7    / 31      same run, earlier sweep collapsed: word salad, 0/40, no tool variety

Three tiers: ok at or below 0.05 (the band the one coherent state occupied), WARN up to
2.0 (degraded but not collapsed: probe before spending eval budget), FAIL above 2.0 or on
any NaN/Inf. The gate is a warning, not a verdict — a canary request costs seconds and
settles what the numbers only flag."""


def dtype_of(archive):
    raw = archive.read('archive/data.pkl').decode('latin1')
    if 'BFloat16Storage' in raw:
        return 'bf16'
    if 'HalfStorage' in raw:
        return 'fp16'
    if 'FloatStorage' in raw:
        return 'fp32'
    raise ValueError(f'{archive.filename}: unrecognised storage dtype')


def decode(raw, dtype):
    if dtype == 'bf16':
        codes = struct.unpack('<%dH' % (len(raw) // 2), raw)
        values = []
        nan = inf = 0
        for code in codes:
            exponent = (code >> 7) & 0xFF
            mantissa = code & 0x7F
            if exponent == 0xFF:
                if mantissa:
                    nan += 1
                else:
                    inf += 1
                values.append(0.0)
                continue
            sign = -1.0 if code >> 15 else 1.0
            values.append(0.0 if exponent == 0 else sign * math.ldexp(mantissa / 128.0 + 1.0, exponent - 127))
        return values, nan, inf
    if dtype == 'fp32':
        codes = struct.unpack('<%df' % (len(raw) // 4), raw)
    else:
        codes = struct.unpack('<%de' % (len(raw) // 2), raw)
    nan = sum(1 for value in codes if value != value)
    inf = sum(1 for value in codes if value in (float('inf'), float('-inf')))
    return [0.0 if value != value or value in (float('inf'), float('-inf')) else value for value in codes], nan, inf


def stats(path):
    with zipfile.ZipFile(path) as archive:
        dtype = dtype_of(archive)
        names = sorted((n for n in archive.namelist() if n.startswith('archive/data/')),
                       key=lambda n: int(n.rsplit('/', 1)[1]))
        tensors = []
        for name in names:
            values, nan, inf = decode(archive.read(name), dtype)
            rms = math.sqrt(sum(v * v for v in values) / len(values))
            tensors.append({'name': name.rsplit('/', 1)[1], 'rms': rms,
                            'max_abs': max(abs(v) for v in values), 'nan': nan, 'inf': inf,
                            'elements': len(values)})
    rms_values = sorted(t['rms'] for t in tensors)
    return {'path': str(path), 'dtype': dtype, 'tensors': tensors,
            'median_rms': rms_values[len(rms_values) // 2],
            'max_abs': max(t['max_abs'] for t in tensors),
            'nan': sum(t['nan'] for t in tensors), 'inf': sum(t['inf'] for t in tensors)}


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=REFERENCE_NOTE)
    parser.add_argument('states', nargs='+', type=Path)
    parser.add_argument('--reference', type=Path, default=None,
                        help='known-good state; gate each candidate against its per-tensor RMS')
    parser.add_argument('--warn-rms', type=float, default=0.05,
                        help='warn above this median RMS (default 0.05, the coherent band)')
    parser.add_argument('--max-rms', type=float, default=2.0,
                        help='fail when median RMS exceeds this absolute ceiling (calibrated default 2.0)')
    parser.add_argument('--max-ratio', type=float, default=None,
                        help='additionally fail when median RMS exceeds the reference by this factor')
    parser.add_argument('--verbose', action='store_true', help='print every tensor')
    args = parser.parse_args()

    reference = stats(args.reference) if args.reference else None
    if reference:
        print(f'reference {Path(reference["path"]).name}: dtype={reference["dtype"]} '
              f'median RMS {reference["median_rms"]:.6f} max|v| {reference["max_abs"]:.4f}')
    failed = False
    for path in args.states:
        report = stats(path)
        ratio = report['median_rms'] / reference['median_rms'] if reference and reference['median_rms'] else None
        verdict = ''
        if report['nan'] or report['inf']:
            verdict = 'FAIL (nan/inf present)'
            failed = True
        elif report['median_rms'] > args.max_rms:
            verdict = f'FAIL (median RMS {report["median_rms"]:.3f} > ceiling {args.max_rms})'
            failed = True
        elif ratio is not None and args.max_ratio is not None and ratio > args.max_ratio:
            verdict = f'FAIL (median RMS {ratio:.0f}x reference)'
            failed = True
        elif report['median_rms'] > args.warn_rms:
            verdict = f'WARN (median RMS {report["median_rms"]:.3f} above coherent band; probe behaviour first)'
        print(f'{path.name}: dtype={report["dtype"]} tensors={len(report["tensors"])} '
              f'median RMS {report["median_rms"]:.6f} max|v| {report["max_abs"]:.4f} '
              f'nan={report["nan"]} inf={report["inf"]}'
              + (f' ratio={ratio:.0f}x' if ratio else '') + (f' -> {verdict}' if verdict else ' -> ok'))
        if args.verbose:
            for tensor in report['tensors']:
                print(f'    {tensor["name"]:>4s} rms {tensor["rms"]:.6f} max|v| {tensor["max_abs"]:.4f}')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
